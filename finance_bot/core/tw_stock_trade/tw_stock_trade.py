import json

import asyncio
import pandas as pd
import uvicorn
from sqlalchemy import text

from finance_bot.core.base import CoreBase
from finance_bot.core.tw_stock_data_sync import MarketData
from finance_bot.core.tw_stock_trade.broker import SinoBroker
from finance_bot.core.tw_stock_trade.strategy.strategy_s2v1 import StrategyS2V1
from finance_bot.infrastructure import infra


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

        for action in actions:
            if action['operation'] == 'sell':
                await infra.notifier.send('賣 {stock_id} {shares} 股 參考價: {price} (理由：{note})\n'.format(**action))
                await asyncio.sleep(1)
                await infra.notifier.send('成交')

        await infra.notifier.send('確認餘額')

        for action in actions:
            if action['operation'] == 'buy':
                await infra.notifier.send('買 {stock_id} {shares} 股 參考價: {price} (理由：{note})\n'.format(**action))
                await asyncio.sleep(1)
                await infra.notifier.send('成交')

        await infra.notifier.send('執行交易成功')
        self.logger.info('執行交易成功 ...')
