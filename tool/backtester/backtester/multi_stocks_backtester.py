import datetime as dt

import pandas as pd

from tool.backtester.broker import Broker
from tool.backtester.data_source.stock_data_source import StockDataSource
from tool.backtester.report.multi_stocks_report import MultiStocksReport


class MultiStocksBacktester:
    data_class = StockDataSource
    broker_class = Broker

    def run(self, init_funds, max_single_position_exposure, strategy_class, start, end):
        start_time = dt.datetime.now()
        start = pd.Timestamp(start)
        end = pd.Timestamp(end)

        data_source = self.data_class(
            start=start,
            end=end,
            all_stock_ids=strategy_class.available_stock_ids if strategy_class.available_stock_ids else None,
        )
        broker = self.broker_class(data_source, init_funds, max_single_position_exposure)

        strategy_map = {}
        for stock_id in data_source.all_stock_ids:
            strategy = strategy_class()
            strategy.stock_id = stock_id
            strategy.broker = broker
            strategy.data_source = data_source
            strategy.pre_handle()

            strategy_map[stock_id] = strategy

        data_source.is_limit = True

        for today in data_source.all_date_range:
            data_source.set_time(today)

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

            broker.settle_date()

            for _, strategy in strategy_map.items():
                strategy.inter_handle()

        print('回測花費時間：', dt.datetime.now() - start_time)

        return MultiStocksReport(
            strategy_name=strategy_class.name,
            data_source=data_source,
            broker=broker,
        )
