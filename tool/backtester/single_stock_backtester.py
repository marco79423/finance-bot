import dataclasses

import pandas as pd
import plotly.graph_objects as go

from finance_bot.core import TWStockManager
from tool.backtester.broker import Broker
from tool.backtester.model import LimitMarketData
from tool.backtester.strategy import SimpleStrategy


@dataclasses.dataclass
class Result:
    strategy_name: str
    init_funds: int
    final_funds: int
    start: pd.Timestamp
    end: pd.Timestamp
    trades: pd.DataFrame
    equity_curve: pd.Series
    data: LimitMarketData

    def show(self):
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None):
            print(self.trades)

        data = [
            go.Candlestick(
                x=self.data.close.index,
                open=self.data.open,
                high=self.data.high,
                low=self.data.low,
                close=self.data.close,
                increasing_line_color='red',
                decreasing_line_color='green',
                name='K 線',
            )
        ]

        for idx, trade in self.trades.iterrows():
            data.append(
                go.Scatter(
                    x=[trade['start_date'], trade['end_date']],
                    y=[trade['start_price'], trade['end_price']],
                    line_color='red' if trade['total_return'] > 0 else 'green',
                    name=f'trade {idx}'
                )
            )

        data.append(
            go.Scatter(
                x=self.equity_curve.index,
                y=self.equity_curve,
                name='權益',
                xaxis="x",
                yaxis="y2"
            )
        )

        fig = go.Figure(
            data=data,
            layout=go.Layout(
                xaxis=dict(
                    title='日期',
                    rangeslider_visible=False,
                ),
                yaxis=dict(
                    title='股價',
                    domain=[0.5, 1],
                ),
                yaxis2=dict(
                    title='權益',
                    domain=[0, 0.5],
                ),
            )
        )

        for _, trade in self.trades.iterrows():
            fig.add_annotation(
                x=trade['start_date'],
                y=trade['start_price'],
                text="Buy",
                arrowhead=2,
                ax=0,
                ay=-30
            )
            fig.add_annotation(
                x=trade['end_date'],
                y=trade['end_price'],
                text="Sell",
                arrowhead=2,
                ax=0,
                ay=-30
            )

        fig.show()


class SingleStockBacktester:
    """

    * 隔天買入最高價
    * 隔天賣出最低價
    """
    fee_discount = 0.6

    def __init__(self, data):
        self.data = data

    def run(self, stock_id, init_funds, strategy_class, start, end):
        start = pd.Timestamp(start)
        end = pd.Timestamp(end)

        broker = Broker(self.data, init_funds, max_single_position_exposure=1)

        strategy_class.stock_id = stock_id
        strategy_class.broker = broker
        strategy = strategy_class()

        all_date_range = self.data.close.loc[start:end].index  # 交易日

        for today in all_date_range:
            broker.begin_date(today)

            holding_stock_ids = broker.holding_stock_ids
            if holding_stock_ids:
                if strategy._sell_next_day_market:
                    broker.sell(stock_id)
            else:
                if strategy._buy_next_day_market:
                    broker.buy(stock_id)

            strategy.inter_clean()
            strategy.handle()

            broker.end_date()

        return Result(
            strategy_name=strategy.name,
            start=start,
            end=end,
            init_funds=init_funds,
            final_funds=broker.funds,
            trades=broker.all_trades,
            data=strategy.data,
            equity_curve=broker.equity_curve
        )


def main():
    backtester = SingleStockBacktester(TWStockManager().data)

    result = backtester.run(
        stock_id='0050',
        init_funds=600000,
        strategy_class=SimpleStrategy,
        start='2015-08-01',
        # start='2015-09-04',
        # end='2015-09-10',
        end='2023-08-10',
    )
    result.show()


if __name__ == '__main__':
    main()
