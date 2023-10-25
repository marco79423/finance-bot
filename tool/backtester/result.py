import abc
import dataclasses

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from tool.backtester.broker import Broker
from tool.backtester.model import LimitMarketData


@dataclasses.dataclass
class ResultBase:
    strategy_name: str
    broker: Broker

    @property
    def init_funds(self):
        return self.broker.init_funds

    @property
    def final_funds(self):
        return self.broker.funds

    @property
    def start(self):
        return self.broker.start_date

    @property
    def end(self):
        return self.broker.current_date

    @property
    def trades(self):
        return self.broker.analysis_trades

    @abc.abstractmethod
    def show(self):
        pass


class MultiStocksResult(ResultBase):

    def show(self):
        print(f'使用策略 {self.strategy_name} 回測結果')
        print(f'回測範圍： {self.start} ~ {self.end}')
        print(f'原始本金： {self.init_funds}')
        print(f'總獲利(含手續費)： {self.broker.total_return}')
        print(f'各倉位狀況：')
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None):
            print(self.trades)

        fig = px.line(
            data_frame=pd.DataFrame({
                '權益': self.broker.equity_curve,
            }),
            title=self.strategy_name
        )
        fig.show()


@dataclasses.dataclass
class SingleStockResult(ResultBase):
    data: LimitMarketData

    def show(self):
        print(f'使用策略 {self.strategy_name} 回測結果')
        print(f'回測範圍： {self.start} ~ {self.end}')
        print(f'原始本金： {self.init_funds}')
        print(f'總獲利(含手續費)： {self.broker.total_return}')
        print(f'各倉位狀況：')

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
                x=self.broker.equity_curve.index,
                y=self.broker.equity_curve,
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
