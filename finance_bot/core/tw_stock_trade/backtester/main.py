from decimal import Decimal

from finance_bot.core.tw_stock_trade.backtester.backtester import Backtester
from finance_bot.core.tw_stock_trade.backtester.reporter.reporter import Reporter
from finance_bot.core.tw_stock_trade.strategy import StrategyS1V0, StrategyNew


def generate_sequence(min_v, max_v, step_v):
    if isinstance(min_v, float):
        data_type = float
    elif isinstance(min_v, int):
        data_type = int
    else:
        raise ValueError('Not supported data type')

    min_v = Decimal(str(min_v))
    max_v = Decimal(str(max_v))
    step_v = Decimal(str(step_v))
    result = []

    while min_v <= max_v:
        result.append(data_type(min_v))
        min_v += step_v

    return result


def generate_strategies(*strategy_map_list) -> list:
    strategies = []
    for strategy_class, factors in strategy_map_list:
        params_list = [{}]

        factor_map = {}
        for factor in factors:
            factor_map[factor['name']] = factor

        for name, factor in factor_map.items():
            new_params_list = []
            for params in params_list:
                for value in generate_sequence(factor['min'], factor['max'], factor['step']):
                    new_params_list.append({**params, name: value})
                if factor.get('dispensable', False):
                    new_params_list.append({**params, name: None})
            params_list = new_params_list

        for params in params_list:
            strategies.append(
                [strategy_class, params]
            )
    return strategies


def main():
    backtester = Backtester()

    strategies = generate_strategies(
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
        # strategies=[
        #     [StrategyS1V0, dict(max_single_position_exposure=0.1)],
        #     [StrategyNew, dict(max_single_position_exposure=0.1)],
        # ],
        strategies=strategies
    )

    reporter = Reporter(results)
    reporter.summary()
    reporter.serve()


if __name__ == '__main__':
    main()
