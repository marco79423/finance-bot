from tool.backtester.backtester import MultiStocksBacktester
from tool.backtester.strategy.strategy_s1v0 import StrategyS1V0


def main():
    backtester = MultiStocksBacktester()

    result = backtester.run(
        init_funds=600000,
        # init_funds=10000000000,
        max_single_position_exposure=0.1,
        # max_single_position_exposure=1,
        # strategy_class=SimpleStrategy,
        strategy_class=StrategyS1V0,
        start='2015-08-01',
        end='2023-08-10',
    )
    result.show()


if __name__ == '__main__':
    main()