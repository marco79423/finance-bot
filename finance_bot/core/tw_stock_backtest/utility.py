from decimal import Decimal


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


def generate_strategy_configs(*strategy_map_list) -> list:
    strategies = []
    for strategy_class, params_configs in strategy_map_list:
        params_list = [{}]

        for name, config in params_configs.items():
            new_params_list = []
            for params in params_list:
                if 'choices' in config:
                    for choice in config['choices']:
                        new_params_list.append({**params, name: choice})
                else:
                    for value in generate_sequence(config['min'], config['max'], config['step']):
                        new_params_list.append({**params, name: value})
                if config.get('dispensable', False):
                    new_params_list.append({**params})
            params_list = new_params_list

        for params in params_list:
            strategies.append(
                [strategy_class, params]
            )
    return strategies
