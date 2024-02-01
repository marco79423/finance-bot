import uvicorn

from finance_bot.core.base import CoreBase
from finance_bot.core.tw_stock_trade.broker import SinoBroker
from finance_bot.core.tw_stock_data_sync import MarketData
from finance_bot.core.tw_stock_trade.strategy.strategy_s2v1 import StrategyS2V1
from finance_bot.infrastructure import infra


class TWStockTrade(CoreBase):
    name = 'tw_stock_trade'

    strategy = StrategyS2V1()

    def __init__(self):
        super().__init__()

        self._broker = SinoBroker()
        self._latest_actions = []

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

    @property
    def get_latest_actions(self):
        return self._latest_actions

    async def execute_trades(self):
        self.logger.info('開始執行交易 ...')
        self.logger.info('執行交易成功 ...')
