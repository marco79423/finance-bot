import uvicorn

from finance_bot.core.base import CoreBase
from finance_bot.core.tw_stock_backtest.backtester import Backtester
from finance_bot.core.tw_stock_backtest.utility import generate_strategies
from finance_bot.core.tw_stock_trade.strategy import StrategyS1V1


class TWStockBacktest(CoreBase):
    name = 'tw_stock_backtest'

    strategy = StrategyS1V1()
    init_balance = 600000
    start = '2015-08-01'
    end = '2023-08-10'

    def start(self):
        self.logger.info(f'啟動 {self.name} ...')
        app = self.get_app()

        @app.on_event("startup")
        async def startup():
            await self.execute_backtest_task()

        uvicorn.run(app, host='0.0.0.0', port=16950)

    async def execute_backtest_task(self):
        self.logger.info('開始執行回測 ...')
        # backtester = Backtester()
        # strategies = generate_strategies(
        #     (self.strategy, [
        #         dict(name='max_single_position_exposure', min=0.1, max=0.3, step=0.1),
        #     ]),
        # )
        #
        # backtester.run(
        #     init_balance=self.init_balance,
        #     start=self.start,
        #     end=self.end,
        #     strategies=strategies
        # )
