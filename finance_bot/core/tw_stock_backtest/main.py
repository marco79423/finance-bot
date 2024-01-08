from decimal import Decimal

from finance_bot.core.tw_stock_backtest.backtester import Backtester
from finance_bot.core.tw_stock_backtest.reporter.reporter import Reporter
from finance_bot.core.tw_stock_backtest.utility import generate_strategy_configs
from finance_bot.core.tw_stock_trade.strategy import StrategyS1V0, StrategyNew, StrategyS1V1


def main():
    backtester = Backtester()

    strategy_configs = generate_strategy_configs(
        (StrategyS1V0, [
            dict(name='max_single_position_exposure', min=0.1, max=0.3, step=0.1),
            dict(name='a', min=1, max=5, step=1, dispensable=True),
        ]),
        (StrategyNew, [
            dict(name='max_single_position_exposure', min=0.1, max=0.3, step=0.1),
        ]),
    )

    results = backtester.run(
        init_balance=600000,
        start='2015-08-01',
        end='2023-08-10',
        # end='2015-12-10',
        strategy_configs=[
            [StrategyS1V0, dict(max_single_position_exposure=0.1)],
            [StrategyS1V1, dict(max_single_position_exposure=0.1)],
            [StrategyS1V1, dict(max_single_position_exposure=0.1, ideal_growth_rate=10, accept_loss_rate=5)],
            [StrategyS1V1, dict(max_single_position_exposure=0.2, ideal_growth_rate=10, accept_loss_rate=5)],
            # [StrategyNew, dict(max_single_position_exposure=0.1)],
        ],
        # strategies=strategies
    )

    reporter = Reporter(results)
    reporter.summary()
    reporter.serve()


if __name__ == '__main__':
    main()
