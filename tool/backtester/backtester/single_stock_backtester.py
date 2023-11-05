import pandas as pd

from finance_bot.core import TWStockManager
from tool.backtester.broker import Broker
from tool.backtester.report.multi_stocks_report import SingleStockReport
from tool.backtester.strategy.strategy_s1v0 import StrategyS1V0


class SingleStockBacktester:
    def __init__(self, data):
        self.data = data

    def run(self, stock_id, init_funds, strategy_class, start, end):
        start = pd.Timestamp(start)
        end = pd.Timestamp(end)

        broker = Broker(self.data, init_funds, max_single_position_exposure=1)

        strategy = strategy_class()
        strategy.stock_id = stock_id
        strategy.broker = broker

        all_date_range = self.data.close.loc[start:end].index  # 交易日

        for today in all_date_range:
            broker.begin_date(today)
            holding_stock_ids = broker.holding_stock_ids
            if holding_stock_ids:
                if strategy._sell_next_day_market:
                    broker.sell(stock_id, note=strategy._sell_next_day_market_note)
            else:
                if strategy._buy_next_day_market:
                    broker.buy(stock_id, note=strategy._buy_next_day_market_note)
            broker.settle_date()

            strategy.inter_handle()

        return SingleStockReport(
            broker=broker,
            strategy_name=strategy.name,
            data=strategy._data,
        )


def main():
    backtester = SingleStockBacktester(TWStockManager().data)

    result = backtester.run(
        stock_id='0050',
        init_funds=600000,
        # strategy_class=SimpleStrategy,
        strategy_class=StrategyS1V0,
        # start='2015-08-01',
        start='2015-09-04',
        # end='2015-09-10',
        end='2023-08-10',
    )
    result.show()


if __name__ == '__main__':
    main()
