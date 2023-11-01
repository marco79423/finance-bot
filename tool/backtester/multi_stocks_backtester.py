import datetime as dt

import pandas as pd

from finance_bot.core import TWStockManager
from tool.backtester.broker import Broker
from tool.backtester.result import MultiStocksResult
from tool.backtester.strategy.strategy_s1v0 import StrategyS1V0


class MultiStocksBacktester:
    def __init__(self, data):
        self.data = data

    def run(self, init_funds, max_single_position_exposure, strategy_class, start, end):
        start_time = dt.datetime.now()
        start = pd.Timestamp(start)
        end = pd.Timestamp(end)

        broker = Broker(self.data, init_funds, max_single_position_exposure)

        all_stock_ids = strategy_class.available_stock_ids
        if not all_stock_ids:
            all_stock_ids = self.data.close.columns

        strategy_map = {}
        for stock_id in all_stock_ids:
            strategy = strategy_class()
            strategy.stock_id = stock_id
            strategy.broker = broker
            strategy_map[stock_id] = strategy
            strategy_map[stock_id].pre_handle()

        all_date_range = self.data.close.loc[start:end].index  # 交易日

        for today in all_date_range:
            broker.begin_date(today)

            holding_stock_ids = broker.holding_stock_ids
            if holding_stock_ids:
                for stock_id, strategy in strategy_map.items():
                    if stock_id in holding_stock_ids and strategy._sell_next_day_market:
                        broker.sell(stock_id, note=strategy._sell_next_day_market_note)

            for stock_id, strategy in strategy_map.items():
                if stock_id not in holding_stock_ids and strategy._buy_next_day_market:
                    ok = broker.buy(stock_id, note=strategy._buy_next_day_market_note)
                    if not ok:
                        break

            broker.end_date()

            for _, strategy in strategy_map.items():
                strategy.inter_handle()

        print('回測花費時間：', dt.datetime.now() - start_time)

        return MultiStocksResult(
            strategy_name=strategy_class.name,
            broker=broker,
        )


def main():
    backtester = MultiStocksBacktester(TWStockManager().data)

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
