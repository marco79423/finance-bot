import decimal

import asyncio
import uvicorn
from shioaji.constant import Status
from sqlalchemy.ext.asyncio import AsyncSession

from finance_bot.core.base import CoreBase
from finance_bot.core.exception import ExecuteError
from finance_bot.core.tw_stock_data_sync import MarketData
from finance_bot.core.tw_stock_trade.broker import SinoBroker
from finance_bot.core.tw_stock_trade.strategy.strategy_t2v2 import StrategyT2V2
from finance_bot.infrastructure import infra
from finance_bot.repository import WalletRepository, TWStockTradeLogRepository, SettingTWStockTradeRepository, \
    TWStockActionRepository


class TWStockTrade(CoreBase):
    name = 'tw_stock_trade'

    strategy = StrategyT2V2()
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
            await self._execute_sell_actions()
            await self._execute_buy_actions()
            self.logger.info('執行交易成功')
            await infra.notifier.send('執行交易成功')
        except:
            self.logger.opt(exception=True).error('執行交易失敗')
            raise ExecuteError()

    async def _execute_sell_actions(self):
        async with AsyncSession(infra.db.async_engine) as session:
            sell_actions = await self._tw_stock_action_repo.get_sell_actions(session)
            # 檢查需不需賣股
            if not sell_actions:
                return

        balance = await self._query_balance()
        await infra.notifier.send(f'進行委託賣股直到成交... [餘額 {int(balance)} 元]')

        for action in sell_actions:
            stock_id = action.stock_id
            shares = action.shares
            note = action.note

            # 委託賣股直到成交
            async with infra.db.async_engine.begin() as session:
                result = await self.sell_market(stock_id=stock_id, shares=shares, note=note)
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
                    shares=shares,
                    price=result['avg_price'],
                    fee=result['total_fee'],
                    amount=result['total'],
                    note=note
                )
        await infra.notifier.send(f'賣股成交完成 [餘額 {int(balance)} 元]')

    async def _execute_buy_actions(self):
        async with AsyncSession(infra.db.async_engine) as session:
            # 檢查需不需買股
            buy_actions = await self._tw_stock_action_repo.get_buy_actions(session)
            if not buy_actions:
                return

        balance = await self._wallet_repo.get_balance(session, code=self.wallet_code)
        await infra.notifier.send(f'進行委託買股直到成交... [餘額 {int(balance)} 元]')

        for action in buy_actions:
            stock_id = action.stock_id
            shares = action.shares
            note = action.note

            # 委託買股直到成交
            async with infra.db.async_engine.begin() as session:
                possible_highest_cost = self._get_possible_highest_cost(stock_id=stock_id, shares=shares)
                if balance < possible_highest_cost:
                    break

                result = await self.buy_market(stock_id=stock_id, shares=shares, note=note)
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
                    shares=shares,
                    price=result['avg_price'],
                    fee=result['total_fee'],
                    amount=result['total'],
                    note=note
                )
        await infra.notifier.send(f'買股成交完成 [餘額 {int(balance)} 元]')

    async def sell_market(self, stock_id, shares, note):
        message = f'賣 {stock_id} {shares} 股'
        if note:
            message += f'(理由：{note})'
        message += '...'
        await infra.notifier.send(message)

        trade = self._broker.sell_market(stock_id=stock_id, shares=shares, note=note)
        while True:
            self._broker.update_status()
            if trade.status.status == Status.Filled:
                break
            elif trade.status.status in [Status.Failed, Status.Cancelled]:
                self.logger.error(trade.status)
                raise ExecuteError()
            await asyncio.sleep(1)

        total = decimal.Decimal(0)
        avg_price = decimal.Decimal(0)
        total_fee = decimal.Decimal(0)
        for deal in trade.status.deals:
            fee = self._broker.commission_info.get_sell_commission(
                deal.price,
                deal.quantity * 1000,
            )
            total += int(deal.price * deal.quantity * 1000) - fee
            avg_price += decimal.Decimal(int(deal.price * (deal.quantity * 1000))) / shares
            total_fee += fee

        message = '賣 {stock_id} {shares} 股 價格 {avg_price} 元 完全成交\n總費用：{total}(手續費：{total_fee})\n'.format(
            stock_id=stock_id,
            avg_price=avg_price,
            shares=shares,
            total=total,
            total_fee=total_fee,
        )
        await infra.notifier.send(message)

        return dict(
            stock_id=stock_id,
            avg_price=avg_price,
            shares=shares,
            total=total,
            total_fee=total_fee,
            description=message,
        )

    async def buy_market(self, stock_id, shares, note):
        message = f'買 {stock_id} {shares} 股'
        if note:
            message += f'(理由：{note})'
        message += '...'
        await infra.notifier.send(message)

        trade = self._broker.buy_market(stock_id=stock_id, shares=shares, note=note)
        while True:
            self._broker.update_status()
            if trade.status.status == Status.Filled:
                break
            elif trade.status.status in [Status.Failed, Status.Cancelled]:
                self.logger.error(trade.status)
                raise ExecuteError()
            await asyncio.sleep(1)

        total = decimal.Decimal(0)
        avg_price = decimal.Decimal(0)
        total_fee = decimal.Decimal(0)

        for deal in trade.status.deals:
            fee = self._broker.commission_info.get_buy_commission(
                deal.price,
                deal.quantity * 1000,
            )
            total += int(deal.price * deal.quantity * 1000) + fee
            avg_price += decimal.Decimal(int(deal.price * (deal.quantity * 1000))) / shares
            total_fee += fee

        message = '買 {stock_id} {shares} 股 價格 {avg_price} 元 完全成交\n費用：{total}(手續費：{total_fee})'.format(
            stock_id=trade.contract.code,
            avg_price=avg_price,
            shares=shares,
            total=total,
            total_fee=total_fee,
        )
        await infra.notifier.send(message)

        return dict(
            stock_id=trade.contract.code,
            avg_price=avg_price,
            shares=shares,
            total=total,
            total_fee=total_fee,
            description=message,
        )

    def _get_possible_highest_cost(self, stock_id, shares):
        highest_price = self._broker.get_today_high_price(stock_id)
        possible_highest_fee = self._broker.commission_info.get_buy_commission(
            price=highest_price,
            shares=shares
        )
        return (shares * highest_price) + possible_highest_fee

    async def _query_balance(self):
        async with AsyncSession(infra.db.async_engine) as session:
            return await self._wallet_repo.get_balance(session, code=self.wallet_code)
