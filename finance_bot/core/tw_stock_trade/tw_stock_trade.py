import json
import traceback

import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession

from finance_bot.core.base import CoreBase
from finance_bot.core.tw_stock_trade.broker import SinoBroker
from finance_bot.core.tw_stock_trade.market_data import MarketData
from finance_bot.core.tw_stock_trade.strategy import StrategyS1V0
from finance_bot.infrastructure import infra
from finance_bot.model.task_status import TaskStatus


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
        await infra.mq.subscribe('tw_stock_trade.execute_strategy', self._execute_strategy_handler)

    async def _execute_strategy_handler(self, sub, data):
        await self.execute_strategy()

    async def execute_strategy(self):
        try:
            self.logger.info('開始執行策略 ...')

            market_data = MarketData()

            self.strategy.market_data = market_data
            self.strategy.broker = self._broker
            self.strategy.pre_handle()
            self.strategy.inter_handle()

            async with AsyncSession(infra.db.async_engine) as session:
                await infra.db.insert_or_update(session, TaskStatus, dict(
                    key='tw_stock_trade.latest_strategy_actions',
                    is_error=False,
                    detail=json.dumps(self.strategy.actions),
                ))

            self.logger.info('執行策略成功')
            return self.strategy.actions
        except:
            async with AsyncSession(infra.db.async_engine) as session:
                await infra.db.insert_or_update(session, TaskStatus, dict(
                    key='tw_stock_trade.latest_strategy_actions',
                    is_error=True,
                    detail=traceback.format_exc(),
                ))
            raise

    @property
    def get_latest_actions(self):
        return self._latest_actions

    async def execute_trades(self):
        self.logger.info('開始執行交易 ...')
        self.logger.info('執行交易成功 ...')
