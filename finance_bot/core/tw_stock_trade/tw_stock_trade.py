import json

import asyncio
import pandas as pd
import uvicorn
from shioaji.constant import Status
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from finance_bot.core.base import CoreBase
from finance_bot.core.tw_stock_data_sync import MarketData
from finance_bot.core.tw_stock_trade.broker import SinoBroker
from finance_bot.core.tw_stock_trade.strategy.strategy_s2v1 import StrategyS2V1
from finance_bot.infrastructure import infra
from finance_bot.model import Wallet


class TWStockTrade(CoreBase):
    name = 'tw_stock_trade'

    strategy = StrategyS2V1()

    def __init__(self):
        super().__init__()

        self._broker = SinoBroker()

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

    async def _update_strategy_actions_handler(self, sub, data):
        await self.execute_task(
            f'最新策略行動更新',
            'tw_stock_trade.update_strategy_actions',
            self.execute_strategy,
            retries=5,
        )

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
        except TimeoutError:
            await infra.notifier.send('超時任務取消')
            for trade in self._broker.trades():
                if trade.status.status != Status.Filled:
                    self._broker.cancel_trade(trade)
                await infra.notifier.send('取消委託 {stock_id}'.format(
                    stock_id=trade.contract.code,
                ))

    async def _execute_trades(self):
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

        with AsyncSession(infra.db.engine) as session:
            balance, = await session.execute(
                select(Wallet.balance)
                .where(Wallet.code == 'sinopac')
                .limit(1)
            ).first()
        await infra.notifier.send(f'當前餘額 {balance} 元')

        buy_actions = []
        sell_actions = []

        for action in actions:
            if action['operation'] == 'sell':
                sell_actions.append(action)
            elif action['operation'] == 'buy':
                buy_actions.append(action)

        # 委託賣股
        trades = []
        message = ''
        for action in sell_actions:
            stock_id = action['stock_id']
            shares = action['shares']
            price = action['price']
            total = action['total']
            note = action['note']

            trade = await self._broker.sell_all_market(stock_id=stock_id, note=note)
            message += '賣 {stock_id} {shares} 股 參考價: {price} 費用： {total} (理由：{note})\n'.format(
                stock_id=stock_id,
                shares=shares,
                price=price,
                total=total,
                note=note,
            )
            trades.append(trade)

        await infra.notifier.send(message)

        # 等待賣股成交
        await asyncio.sleep(5)
        while not all(trade.status.status == Status.Filled for trade in trades):
            self._broker.update_status()
            await asyncio.sleep(5)

        message = ''
        for trade in trades:
            total = 0
            total_shares = 0
            for deal in trade.status.deals:
                shares = deal.quantity * 1000
                total += deal.price * shares - self._broker.commission_info.get_sell_commission(
                    deal.price,
                    shares,
                )
                total_shares += shares

            balance += total
            message += '賣 {stock_id} {price} 元 {shares} 股完全成交 費用：{total}\n'.format(
                stock_id=trade.contract.code,
                price=total / total_shares,
                shares=total_shares,
                total=total,
            )
        message += '新餘額 {balance} 元'
        await infra.notifier.send(message)

        # 委託買股直到成交
        for action in buy_actions:
            stock_id = action['stock_id']
            price = action['price']
            shares = action['shares']
            note = action['note']

            high_price = self._broker.get_high_price(stock_id)
            possible_highest_cost = (shares * high_price) + self._broker.commission_info.get_buy_commission(
                price=high_price,
                shares=shares
            )

            if balance < possible_highest_cost:
                break

            await infra.notifier.send(
                '買 {stock_id} {shares} 股 參考價: {price} (最高 {high_price}) (理由：{note})\n'.format(
                    stock_id=stock_id,
                    shares=shares,
                    price=price,
                    high_price=high_price,
                    note=note,
                )
            )

            trade = await self._broker.buy_market(stock_id=stock_id, shares=shares, note=note)
            while True:
                self._broker.update_status()
                if trade.status.status == Status.Filled:
                    break
                await asyncio.sleep(1)

            total = 0
            total_shares = 0
            for deal in trade.status.deals:
                shares = deal.quantity * 1000
                total += deal.price * shares + self._broker.commission_info.get_buy_commission(
                    deal.price,
                    deal.quantity * 1000,
                )
                total_shares += shares

            await infra.notifier.send('買 {stock_id} {price} 元 {shares} 股完全成交 費用：{total}\n'.format(
                stock_id=trade.contract.code,
                price=total / total_shares,
                shares=total_shares,
                total=total,
            ))
            balance -= total

        with AsyncSession(infra.db.engine) as session:
            await infra.db.insert_or_update(session, Wallet, dict(
                code='sinopac',
                name='永豐活存',
                currency_code='TWD',
                balance=balance
            ))

        await infra.notifier.send('執行交易成功')
        self.logger.info('執行交易成功 ...')
