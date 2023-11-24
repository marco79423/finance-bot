from tool.backtester.backtester import Backtester
from tool.backtester.reporter.reporter import Reporter
from tool.backtester.strategy import StrategyNew, StrategyS1V0


def main():
    backtester = Backtester()

    results = backtester.run(
        init_funds=600000,
        start='2015-08-01',
        end='2023-08-10',
        # end='2015-12-10',
        strategies=[
            [StrategyS1V0, dict(max_single_position_exposure=0.1)],
            [StrategyNew, dict(max_single_position_exposure=0.1)],
        ],
    )

    reporter = Reporter(results)
    reporter.summary()
    reporter.serve()


if __name__ == '__main__':
    main()
