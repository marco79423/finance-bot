import abc
import dataclasses

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dash_table, dcc

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
        print(f'總獲利(含手續費)： {self.broker.total_return:.0f}')
        avg_days = self.trades['period'].mean()
        max_days = self.trades['period'].max()
        min_days = self.trades['period'].min()
        print(f'平均天數： {avg_days:.1f} 天 (最長: {max_days:.1f} 天, 最短: {min_days:.1f}) 天')
        print(f'年化報酬率(含手續費)： {self.broker.annualized_return_rate_with_fee * 100:.2f}%')

        df = self.trades
        df['total_return_rate (fee)'] = df['total_return_rate (fee)'].apply(lambda x: f'{x * 100:.2f}%')
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None):
            print(df)

        array = [
            html.Header(children=self.strategy_name),
            html.Div(children=f'回測範圍： {self.start} ~ {self.end}'),
            html.Div(children=f'原始本金： {self.init_funds}'),
            html.Div(children=f'總獲利(含手續費)： {self.broker.total_return:.0f}'),
            html.Div(children=f'平均天數： {avg_days:.1f} 天 (最長: {max_days:.1f} 天, 最短: {min_days:.1f}) 天'),
            html.Div(children=f'年化報酬率(含手續費)： {self.broker.annualized_return_rate_with_fee * 100:.2f}%'),
            dcc.Graph(figure=px.line(
                data_frame=pd.DataFrame({
                    '權益': self.broker.equity_curve,
                }),
            )),
            dash_table.DataTable(data=df.to_dict('records')),
        ]

        stock_ids = df['stock_id'].unique()
        for stock_id in stock_ids:
            data = self.broker.stock_data(stock_id)

            fig_data = [
                go.Candlestick(
                    x=data.close.index,
                    open=data.open,
                    high=data.high,
                    low=data.low,
                    close=data.close,
                    increasing_line_color='red',
                    decreasing_line_color='green',
                    name='K 線',
                )
            ]

            trades = df[df['stock_id'] == stock_id]
            for idx, trade in trades.iterrows():
                fig_data.append(
                    go.Scatter(
                        x=[trade['start_date'], trade['end_date']],
                        y=[trade['start_price'], trade['end_price']],
                        line_color='red' if trade['total_return'] > 0 else 'green',
                        name=f'trade {idx}'
                    )
                )

            fig = go.Figure(
                data=fig_data,
                layout=go.Layout(
                    xaxis=dict(
                        title='日期',
                        rangeslider_visible=False,
                    ),
                    yaxis=dict(
                        title='股價',
                        domain=[0.5, 1],
                    ),
                )
            )

            for _, trade in trades.iterrows():
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

            array.extend([
                html.Div(children=stock_id),
                dcc.Graph(figure=fig),
                dash_table.DataTable(data=trades.to_dict('records')),
            ])

        app = Dash(__name__)
        app.layout = html.Div(array)
        app.run(debug=True)


@dataclasses.dataclass
class SingleStockResult(ResultBase):
    data: LimitMarketData

    def show(self):
        print(f'使用策略 {self.strategy_name} 回測結果')
        print(f'回測範圍： {self.start} ~ {self.end}')
        print(f'原始本金： {self.init_funds}')
        print(f'總獲利(含手續費)： {self.broker.total_return}')
        print(f'年化報酬率(含手續費)： {self.broker.annualized_return_rate_with_fee}')
        avg_days = self.trades['period'].mean()
        max_days = self.trades['period'].max()
        min_days = self.trades['period'].min()
        print(f'平均天數： {avg_days:.1f} 天 (最長: {max_days:.1f} 天, 最短: {min_days:.1f}) 天')
        print(f'各倉位狀況：')

        df = self.trades
        df['total_return_rate (fee)'] = df['total_return_rate (fee)'].apply(lambda x: f'{x * 100:.2f}%')
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None):
            print(df)

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