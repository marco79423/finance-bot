import decimal
import json

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
from finance_bot.core.tw_stock_trade.strategy.strategy_s2v1 import StrategyS2V1
from finance_bot.infrastructure import infra
from finance_bot.repository import WalletRepository


class TWStockTrade(CoreBase):
    name = 'tw_stock_trade'

    strategy = StrategyS2V1()

    def __init__(self):
        super().__init__()

        self._broker = SinoBroker()
        self._wallet_repo = WalletRepository()

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

    async def _update_strategy_actions_handler(self, sub, data):
        await self.execute_task(
            f'最新策略行動更新',
            'tw_stock_trade.update_strategy_actions',
            self.execute_strategy,
            retries=5,
        )

    async def _execute_trades_handler(self, sub, data):
        await self.execute_trades()

    async def execute_strategy(self):
        self.logger.info('開始執行策略 ...')

        self._broker.refresh()

        market_data = MarketData()
        self.strategy.market_data = market_data
        self.strategy.broker = self._broker
        self.strategy.pre_handle()
        self.strategy.inter_handle()

        self.logger.info('執行策略成功')
        return self.strategy.actions

    async def execute_trades(self):
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
        task_status_df = pd.read_sql(
            sql=text("SELECT * FROM task_status"),
            con=infra.db.engine,
            index_col='key',
            parse_dates=['created_at', 'updated_at'],
            dtype={
                'is_error': bool,
            }
        )

        key = 'tw_stock_trade.update_strategy_actions'
        if key not in task_status_df.index:
            await infra.notifier.send('交易策略不存在')
            return

        row = task_status_df.loc[key]
        if row['is_error']:
            await infra.notifier.send('交易策略異常')
            return

        actions = json.loads(row['detail'])
        if not actions:
            await infra.notifier.send('沒有要執行的交易')
            return

        async with (AsyncSession(infra.db.async_engine) as session):
            balance = await self._wallet_repo.get_balance(session, code='sinopac')
        await infra.notifier.send(f'當前餘額 {balance} 元')

        buy_actions = []
        sell_actions = []

        for action in actions:
            if action['operation'] == 'sell':
                sell_actions.append(action)
            elif action['operation'] == 'buy':
                buy_actions.append(action)

        # 委託賣股直到成交
        if sell_actions:
            await infra.notifier.send('進行委託賣股直到成交')
            for action in sell_actions:
                result = await self.sell_market(
                    stock_id=action['stock_id'],
                    shares=action['shares'],
                    note=action['note']
                )
                balance += result['total']

                async with AsyncSession(infra.db.async_engine) as session:
                    await self._wallet_repo.set_balance(
                        session=session,
                        code='sinopac',
                        balance=balance,
                        description=result['description']
                    )

            await infra.notifier.send(f'賣股後新餘額 {balance} 元')

        if buy_actions:
            # 委託買股直到成交
            await infra.notifier.send('委託買股直到成交')
            for action in buy_actions:
                high_price = self._broker.get_today_high_price(action['stock_id'])
                possible_highest_cost = (action['shares'] * high_price) + self._broker.commission_info.get_buy_commission(
                    price=high_price,
                    shares=action['shares']
                )

                if balance < possible_highest_cost:
                    break

                result = await self.buy_market(
                    stock_id=action['stock_id'],
                    shares=action['shares'],
                    note=action['note']
                )

                balance -= result['total']
                async with AsyncSession(infra.db.async_engine) as session:
                    await self._wallet_repo.set_balance(
                        session=session,
                        code='sinopac',
                        balance=balance,
                        description=result['description']
                    )

        await infra.notifier.send('執行交易成功')
        self.logger.info('執行交易成功 ...')

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
            total=total,
            avg_price=avg_price,
            total_price=total_fee,
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
            total=total,
            avg_price=avg_price,
            total_price=total_fee,
            description=message,
        )