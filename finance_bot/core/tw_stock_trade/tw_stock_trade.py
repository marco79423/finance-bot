import pandas as pd
import uvicorn

from finance_bot.core.base import CoreBase
from finance_bot.core.tw_stock_trade.backtester.data_source import DataSource
from finance_bot.core.tw_stock_trade.broker import SinoBroker
from finance_bot.core.tw_stock_trade.strategy import StrategyS1V0
from finance_bot.infrastructure import infra


class TWStockTrade(CoreBase):
    name = 'tw_stock_trade'

    strategy = StrategyS1V0()

    def __init__(self):
        super().__init__()

        self._broker = SinoBroker()
        self._latest_actions = []

    @property
    def account_balance(self):
        return self._broker.current_balance

    @property
    def current_holding(self):
        return self._broker.current_holding

    def start(self):
        self.logger.info(f'啟動 {self.name} ...')
        app = self.get_app()

        @app.on_event("startup")
        async def startup():
            await self.listen()

        uvicorn.run(app, host='0.0.0.0', port=16940)

    async def listen(self):
        await infra.mq.subscribe('tw_stock_trade.execute_strategy', self.execute_strategy)

    async def execute_strategy(self):
        self.logger.info('開始執行策略 ...')
        data_source = DataSource()  # 時間會有問題
        self.strategy.data_source = data_source
        self.strategy.broker = self._broker
        self.strategy.pre_handle()
        self.strategy.inter_handle()
        self._latest_actions = {
            'execute_time': pd.Timestamp(),
            'actions': self.strategy.actions,
        }
        self.logger.info('執行策略成功')

    @property
    def get_latest_actions(self):
        return self._latest_actions

    async def execute_trades(self):
        self.logger.info('開始執行交易 ...')
        self.logger.info('執行交易成功 ...')
