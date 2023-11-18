import datetime as dt

import pandas as pd

from tool.backtester.backtester.result import Result
from tool.backtester.broker import Broker
from tool.backtester.data_source.stock_data_source import StockDataSource


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

        strategy = strategy_class()
        strategy.broker = broker
        strategy.data_source = data_source
        strategy.pre_handle()

        data_source.is_limit = True

        for today in data_source.all_date_range:
            print(today)
            data_source.set_time(today)

            for action in strategy.actions:
                if action['operation'] == 'buy':
                    broker.buy(stock_id=action['stock_id'], note=action['note'])
                elif action['operation'] == 'sell':
                    broker.sell(stock_id=action['stock_id'], note=action['note'])
            strategy.inter_handle()

        print('回測花費時間：', dt.datetime.now() - start_time)

        return Result(
            strategy_name=strategy_class.name,
            init_funds=init_funds,
            final_funds=broker.funds,
            start_time=start,
            end_time=end,
            trade_logs=broker.trade_logs,
        )
