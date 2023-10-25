import dataclasses

import pandas as pd
import plotly.express as px

from finance_bot.core import TWStockManager
from tool.backtester.broker import Broker
from tool.backtester.strategy.strategy_s1v0 import StrategyS1V0


@dataclasses.dataclass
class Result:
    strategy_name: str
    init_funds: int
    final_funds: int
    start: pd.Timestamp
    end: pd.Timestamp
    trades: pd.DataFrame
    equity_curve: pd.Series

    def show(self):
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None):
            print(self.trades)

        fig = px.line(
            data_frame=pd.DataFrame({
                '權益': self.equity_curve,
            }),
            title=self.strategy_name
        )
        fig.show()


class MultiStocksBacktester:
    """

    * 隔天買入漲停價
    * 隔天賣出跌停價
    """
    fee_discount = 0.6

    def __init__(self, data):
        self.data = data

    def run(self, init_funds, max_single_position_exposure, strategy_class, start, end):
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

        return Result(
            strategy_name=strategy_class.name,
            start=start,
            end=end,
            init_funds=init_funds,
            final_funds=broker.funds,
            trades=broker.all_trades,
            equity_curve=broker.equity_curve
        )


def main():
    backtester = MultiStocksBacktester(TWStockManager().data)

    result = backtester.run(
        # init_funds=600000,
        init_funds=10000000000,
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
