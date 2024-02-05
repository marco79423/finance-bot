from finance_bot.core.tw_stock_backtest.backtester import Backtester
from finance_bot.core.tw_stock_backtest.reporter.reporter import Reporter
from finance_bot.core.tw_stock_backtest.utility import generate_strategy_configs
from finance_bot.core.tw_stock_trade.strategy.strategy_s2v0 import StrategyS2V0
from finance_bot.core.tw_stock_trade.strategy.strategy_s2v1 import StrategyS2V1


def main():
    backtester = Backtester()

    strategy_configs = generate_strategy_configs(
        (StrategyS2V0, {}),
        (StrategyS2V1, {
            'max_single_position_exposure': 0.1,
            # 'sma_short': dict(min=5, max=60, step=5),
            # 'sma_long': dict(min=20, max=120, step=5),
            # 'mrs_num': dict(choices=[90, 120]),
            'mrs_num': 120
        }),
    )

    results = backtester.run(
        init_balance=300000,
        start='2015-08-01',
        end='2023-08-10',
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
