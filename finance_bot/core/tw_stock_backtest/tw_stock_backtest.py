import asyncio
import uvicorn

from finance_bot.core.base import CoreBase
from finance_bot.core.tw_stock_backtest.backtester import Backtester
from finance_bot.core.tw_stock_backtest.utility import generate_strategy_configs
from finance_bot.core.tw_stock_trade.strategy import StrategyS1V1


class TWStockBacktest(CoreBase):
    name = 'tw_stock_backtest'

    strategy_class = StrategyS1V1
    init_balance = 600000
    start_time = '2015-08-01'
    end_time = '2023-08-10'

    def start(self):
        self.logger.info(f'啟動 {self.name} ...')
        app = self.get_app()

        @app.on_event("startup")
        async def startup():
            asyncio.create_task(asyncio.to_thread(self.execute_backtest_task))

        uvicorn.run(app, host='0.0.0.0', port=16950)

    def execute_backtest_task(self):
        backtester = Backtester()
        strategy_configs = generate_strategy_configs(
            (self.strategy_class, {
                'max_single_position_exposure': dict(min=0.1, max=0.3, step=0.1),
            })
        )

        for [strategy_class, params] in strategy_configs:
            params_key = ', '.join(f'{k}={params[k]}' for k in sorted(params))
            self.logger.info(f'開始執行回測 {strategy_class.name} <{params_key}>...')
            backtester.run_task(
                init_balance=self.init_balance,
                start=self.start_time,
                end=self.end_time,
                strategy_class=strategy_class,
                params=params,
            )
            self.logger.info(f'回測 {strategy_class.name} <{params_key}> 完成')
