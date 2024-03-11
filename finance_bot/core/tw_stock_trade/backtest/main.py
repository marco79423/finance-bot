from finance_bot.core.tw_stock_trade.backtest.backtester import Backtester
from finance_bot.core.tw_stock_trade.backtest.utility import generate_strategy_configs
from finance_bot.core.tw_stock_trade.reporter.reporter import Reporter
from finance_bot.core.tw_stock_trade.strategy import StrategyT2V0, StrategyT2V1, StrategyT2V2, StrategyT2V3


def main():
    backtester = Backtester()

    strategy_configs = generate_strategy_configs(
        (StrategyT2V0, {}),
        (StrategyT2V1, {}),
        (StrategyT2V2, {}),
        (StrategyT2V3, {
            # 'max_single_position_exposure': 0.1,
            # 'sma_short': dict(min=5, max=60, step=5),
            # 'sma_long': dict(min=20, max=120, step=5),
            # 'mrs_num': dict(choices=[90, 120]),
            # 'sma_out': dict(choices=[20, 40]),
            # 'market_over': dict(min=20, max=120, step=20),
        }),
    )

    results = backtester.run(
        init_balance=500000,
        # start='2015-08-01',
        # end='2023-08-10',

        # start='2023-01-01',
        # end='2023-12-29',

        # start='2022-01-01',
        # end='2022-12-30',

        # start='2021-01-01',
        # end='2021-12-30',

        start='2008-01-01',
        end='2024-01-26',

        strategy_configs=strategy_configs
    )

    reporter = Reporter(results)
    reporter.summary()
    reporter.serve()

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


if __name__ == '__main__':
    main()
