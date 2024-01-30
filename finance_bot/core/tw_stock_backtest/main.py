import pandas as pd
from sqlalchemy import text

from finance_bot.core.tw_stock_backtest.backtester import Backtester
from finance_bot.core.tw_stock_backtest.reporter.reporter import Reporter
from finance_bot.core.tw_stock_backtest.utility import generate_strategy_configs
from finance_bot.core.tw_stock_trade.strategy import StrategyS1V0, StrategyS1V1
from finance_bot.core.tw_stock_trade.strategy.strategy_s2v0 import StrategyS2V0
from finance_bot.infrastructure import infra


def main():
    backtester = Backtester()

    task_stock_tag_df = pd.read_sql(
        sql=text("SELECT DISTINCT name FROM tw_stock_tag"),
        con=infra.db.engine,
    )

    strategy_configs = generate_strategy_configs(
        # (StrategyS1V0, {
        #     'max_single_position_exposure': dict(min=0.1, max=0.3, step=0.1),
        #     'st_tag': dict(choices=task_stock_tag_df['name'].tolist()),
        # }),
        # (StrategyS1V1, {
        #     'max_single_position_exposure': dict(min=0.1, max=0.3, step=0.1),
        #     'st_tag': dict(choices=task_stock_tag_df['name'].tolist()),
        # }),
        (StrategyS2V0, {
            'max_single_position_exposure': 0.1,
            # 'sma_short': dict(min=5, max=60, step=5),
            # 'sma_long': dict(min=20, max=120, step=5),
            'mrs_num': dict(choices=[90, 120]),
        }),
    )

    results = backtester.run(
        init_balance=600000,
        start='2015-08-01',
        end='2023-08-10',

        # start='2024-01-01',
        # end='2024-01-23',
        # /
        strategy_configs=strategy_configs
    )

    # backtester.run_task(
    #     init_balance=600000,
    #     start='2015-08-01',
    #     end='2023-08-10',
    #     strategy_class=StrategyS2V0,
    #     params={
    #         'max_single_position_exposure': 0.1,
    #         # 'sma_short': dict(min=5, max=60, step=5),
    #         # 'sma_long': dict(min=20, max=120, step=5),
    #         # 'mrs_num': dict(choices=[90, 120]),
    #     },
    # )

    reporter = Reporter(results)
    reporter.summary()
    reporter.serve()


if __name__ == '__main__':
    main()
