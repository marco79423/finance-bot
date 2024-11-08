import asyncio

import pandas as pd
import uvicorn
from shioaji.constant import Status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from finance_bot.core.base import CoreBase
from finance_bot.core.exception import ExecuteError
from finance_bot.core.tw_stock_data_sync import MarketData
from finance_bot.core.tw_stock_trade.broker import SinoBroker
from finance_bot.core.tw_stock_trade.strategy import StrategyT2V4
from finance_bot.infrastructure import infra
from finance_bot.repository import WalletRepository, TWStockTradeLogRepository, SettingTWStockTradeRepository, \
    TWStockActionRepository


class TWStockTrade(CoreBase):
    name = 'tw_stock_trade'

    strategy = StrategyT2V4()
    wallet_code = 'sinopac'

    def __init__(self):
        super().__init__()

        self._broker = SinoBroker()
        self._setting_repo = SettingTWStockTradeRepository()
        self._wallet_repo = WalletRepository()
        self._tw_stock_action_repo = TWStockActionRepository()
        self._tw_stock_trade_log_repo = TWStockTradeLogRepository()

    @property
    def account_balance(self):
        return self._broker.current_balance

    @property
    def positions(self):
        return self._broker.positions

    def start(self):
        self.logger.info(f'啟動 {self.name} ...')
        app = self.get_app()

        @app.on_event("startup")
        async def startup():
            await self.listen()

        uvicorn.run(app, host='0.0.0.0', port=16940)

    async def listen(self):
        await infra.mq.subscribe('tw_stock_trade.update_strategy_actions', self._update_strategy_actions_handler)
        await infra.mq.subscribe('tw_stock_trade.execute_trades', self._execute_trades_handler)

    async def increase_balance(self, amount, reason):
        async with AsyncSession(infra.db.async_engine) as session:
            await self._wallet_repo.increase_balance(session=session, code=self.wallet_code, amount=amount,
                                                     description=reason)
            await session.commit()

    async def decrease_balance(self, amount, reason):
        async with AsyncSession(infra.db.async_engine) as session:
            await self._wallet_repo.decrease_balance(session=session, code=self.wallet_code, amount=amount,
                                                     description=reason)
            await session.commit()

    async def set_balance(self, balance, reason):
        async with AsyncSession(infra.db.async_engine) as session:
            await self._wallet_repo.set_balance(session=session, code=self.wallet_code, balance=balance,
                                                description=reason)
            await session.commit()

    async def _update_strategy_actions_handler(self, sub, data):
        await self.execute_task(
            f'最新策略行動更新',
            'tw_stock_trade.update_strategy_actions',
            self.update_actions,
            retries=5,
        )

    async def _execute_trades_handler(self, sub, data):
        await self.execute_trade_task()

    async def update_actions(self):
        self.logger.info('開始更新策略行動 ...')
        self._broker.refresh()
        market_data = MarketData()
        self.strategy.market_data = market_data
        self.strategy.broker = self._broker
        self.strategy.pre_handle()
        self.strategy.inter_handle()
        self._broker.logout()

        async with AsyncSession(infra.db.async_engine) as session:
            await self._tw_stock_action_repo.set_actions(session, self.strategy.actions)
            await session.commit()
        self.logger.info('開始更新策略行動成功')
        return self.strategy.actions

    async def execute_trade_task(self):
        # 確認需不需要執行交易
        async with AsyncSession(infra.db.async_engine) as session:
            enabled = await self._setting_repo.is_auto_trade_enabled(session)
            if not enabled:
                await infra.notifier.send(f'台股交易功能沒有啟動')
                return

        # 檢查是否異常
        task_status_df = pd.read_sql(
            sql=text("SELECT * FROM task_status"),
            con=infra.db.engine,
            dtype={
                'is_error': bool,
            }
        )
        if task_status_df['is_error'].any():
            await infra.notifier.send(f'資料異常，台股交易功能停止交易')
            return

        # 更新策略
        await self.update_actions()

        try:
            await asyncio.wait_for(self._execute_trades(), timeout=60 * 30)
        except ExecuteError:
            await infra.notifier.send('任務失敗取消')
            for trade in self._broker.trades():
                if trade.status.status != Status.Filled:
                    self._broker.cancel_trade(trade)
                await infra.notifier.send('取消委託 {stock_id}'.format(
                    stock_id=trade.contract.code,
                ))
        except TimeoutError:
            await infra.notifier.send('超時任務取消')
            for trade in self._broker.trades():
                if trade.status.status != Status.Filled:
                    self._broker.cancel_trade(trade)
                await infra.notifier.send('取消委託 {stock_id}'.format(
                    stock_id=trade.contract.code,
                ))

    async def _execute_trades(self):
        self.logger.info('重新連線 ...')
        self._broker.login()

        self.logger.info('開始執行交易 ...')
        try:
            async with AsyncSession(infra.db.async_engine) as session:
                await self._execute_sell_actions(session)
                await self._execute_buy_actions(session)
            self.logger.info('執行交易成功')
            await infra.notifier.send('執行交易成功')
        except:
            self.logger.opt(exception=True).error('執行交易失敗')
            raise ExecuteError()
        finally:
            self._broker.logout()

    async def _execute_sell_actions(self, session):
        sell_actions = await self._tw_stock_action_repo.get_sell_actions(session)

        # 檢查需不需賣股
        if not sell_actions:
            return

        balance = await self._wallet_repo.get_balance(session, code=self.wallet_code)
        await infra.notifier.send(f'進行委託賣股直到成交... [餘額 {int(balance)} 元]')

        for stock_id, shares, note in [(action.stock_id, action.shares, action.note) for action in sell_actions]:
            # 委託賣股直到成交
            results = await self.sell_market(stock_id=stock_id, shares=shares, note=note)
            for result in results:
                balance += result['total']

                await self._wallet_repo.set_balance(
                    session=session,
                    code=self.wallet_code,
                    balance=balance,
                    description=result['description']
                )
                await self._tw_stock_trade_log_repo.add_log(
                    session=session,
                    wallet_code=self.wallet_code,
                    strategy_name=self.strategy.name,
                    action='sell',
                    stock_id=stock_id,
                    shares=result['shares'],
                    price=result['avg_price'],
                    fee=result['fee'],
                    amount=result['total'],
                    note=note
                )
            await session.commit()

        await infra.notifier.send(f'賣股成交完成 [餘額 {int(balance)} 元]')

    async def _execute_buy_actions(self, session):
        buy_actions = await self._tw_stock_action_repo.get_buy_actions(session)

        # 檢查需不需買股
        if not buy_actions:
            return

        balance = await self._wallet_repo.get_balance(session, code=self.wallet_code)
        await infra.notifier.send(f'進行委託買股直到成交... [餘額 {int(balance)} 元]')

        for stock_id, shares, note in [(action.stock_id, action.shares, action.note) for action in buy_actions]:
            possible_highest_cost = self._get_possible_highest_cost(stock_id=stock_id, shares=shares)
            if balance < possible_highest_cost:
                await infra.notifier.send(f'餘額無法確保買到 {stock_id} 因此放棄買入')
                break

            # 委託買股直到成交
            results = await self.buy_market(stock_id=stock_id, shares=shares, note=note)
            for result in results:
                balance -= result['total']

                await self._wallet_repo.set_balance(
                    session=session,
                    code=self.wallet_code,
                    balance=balance,
                    description=result['description']
                )
                await self._tw_stock_trade_log_repo.add_log(
                    session=session,
                    wallet_code=self.wallet_code,
                    strategy_name=self.strategy.name,
                    action='buy',
                    stock_id=stock_id,
                    shares=result['shares'],
                    price=result['avg_price'],
                    fee=result['fee'],
                    amount=-result['total'],
                    note=note
                )
            await session.commit()
        await infra.notifier.send(f'買股成交完成 [餘額 {int(balance)} 元]')

    async def sell_market(self, stock_id, shares, note):
        message = f'賣 {stock_id} {shares} 股'
        if note:
            message += f'(理由：{note})'
        message += '...'
        await infra.notifier.send(message)

        self._broker.update_status()
        trade = self._broker.sell_market(stock_id=stock_id, shares=shares, note=note)
        while True:
            self._broker.update_status()
            if trade.status.status == Status.Filled:
                break
            elif trade.status.status in [Status.Failed, Status.Cancelled]:
                self.logger.error(trade.status)
                raise ExecuteError()
            await asyncio.sleep(1)

        deal_price_map = {}
        for deal in trade.status.deals:
            if deal.price not in deal_price_map:
                deal_price_map[deal.price] = 0
            deal_price_map[deal.price] += deal.quantity

        trades = []
        for price, quantity in deal_price_map.items():
            deal_shares = quantity * 1000
            deal_total = int(price * deal_shares)
            deal_avg_price = round(deal_total / deal_shares, 2)
            deal_fee = self._broker.commission_info.get_sell_commission(deal_total)
            deal_total -= deal_fee

            message = '賣 {stock_id} {shares} 股 價格 {avg_price} 元 完全成交\n總費用：{total}(手續費：{fee})\n'.format(
                stock_id=stock_id,
                avg_price=deal_avg_price,
                shares=deal_shares,
                total=deal_total,
                fee=deal_fee,
            )
            await infra.notifier.send(message)

            trades.append(dict(
                stock_id=stock_id,
                avg_price=deal_avg_price,
                shares=deal_shares,
                total=deal_total,
                fee=deal_fee,
                description=message,
            ))

        return trades

    async def buy_market(self, stock_id, shares, note):
        message = f'買 {stock_id} {shares} 股'
        if note:
            message += f'(理由：{note})'
        message += '...'
        await infra.notifier.send(message)

        self._broker.update_status()
        trade = self._broker.buy_market(stock_id=stock_id, shares=shares, note=note)
        while True:
            self._broker.update_status()
            if trade.status.status == Status.Filled:
                break
            elif trade.status.status in [Status.Failed, Status.Cancelled]:
                self.logger.error(trade.status)
                raise ExecuteError()
            await asyncio.sleep(1)

        deal_price_map = {}
        for deal in trade.status.deals:
            if deal.price not in deal_price_map:
                deal_price_map[deal.price] = 0
            deal_price_map[deal.price] += deal.quantity

        trades = []
        for price, quantity in deal_price_map.items():
            deal_shares = quantity * 1000
            deal_total = int(price * deal_shares)
            deal_avg_price = round(deal_total / deal_shares, 2)
            deal_fee = self._broker.commission_info.get_buy_commission(deal_total)
            deal_total += deal_fee

            message = '買 {stock_id} {shares} 股 價格 {avg_price} 元 完全成交\n費用：{total}(手續費：{fee})'.format(
                stock_id=trade.contract.code,
                avg_price=deal_avg_price,
                shares=deal_shares,
                total=deal_total,
                fee=deal_fee,
            )
            await infra.notifier.send(message)

            trades.append(dict(
                stock_id=trade.contract.code,
                avg_price=deal_avg_price,
                shares=deal_shares,
                total=deal_total,
                fee=deal_fee,
                description=message,
            ))
        return trades

    def _get_possible_highest_cost(self, stock_id, shares):
        highest_price = self._broker.get_today_high_price(stock_id)
        possible_highest_fee = self._broker.commission_info.get_buy_commission(highest_price * shares)
        return (shares * highest_price) + possible_highest_fee
