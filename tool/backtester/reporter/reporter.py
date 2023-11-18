import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dash_table, dcc, callback, Output, Input

from tool.backtester.backtester.result import Result
from tool.backtester.data_source import StockDataSource


class Reporter:
    data_class = StockDataSource

    def __init__(self):
        self.data_source = self.data_class()

    def show(self, result: Result):
        trade_logs = self._generate_trade_logs(result)
        trades = self._generate_trades(result)
        equity_curve = self._calculate_equity_curve(result)
        final_equity = equity_curve.iloc[-1]

        print(f'使用策略 {result.strategy_name} 回測結果')
        print(f'回測範圍： {result.start_time} ~ {result.end_time}')
        print(f'原始本金： {result.init_funds} 元')
        print(f'最終本金： {result.final_funds}')
        print(f'最終權益： {final_equity} 元')

        total_return = trades['total_return'].sum()
        total_return_with_fee = trades['total_return (fee)'].sum()
        print(f'總獲利： {total_return} 元')
        print(f'總獲利(含手續費)： {total_return_with_fee} 元')

        avg_days = trades['period'].mean()
        max_days = trades['period'].max()
        min_days = trades['period'].min()
        print(f'平均天數： {avg_days:.1f} 天 (最長: {max_days:.1f} 天, 最短: {min_days:.1f}) 天')

        total_return_rate_with_fee = total_return_with_fee / result.init_funds
        print(f'報酬率： {total_return_rate_with_fee * 100:.2f}%')

        hold_year = (result.end_time - result.start_time).days / 365.25
        annualized_return_rate_with_fee = (1 + total_return_rate_with_fee) ** (1 / hold_year) - 1
        print(f'年化報酬率(含手續費)： {annualized_return_rate_with_fee * 100:.2f}%')

        # print(f'各倉位狀況：')
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None):
        #     print(df)

        # print(f'交易紀錄：')
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None):
        #     print(self.trade_logs)

        array = [
            html.Header(children=result.strategy_name),
            html.Div(children=f'回測範圍： {result.start_time} ~ {result.end_time}'),
            html.Div(children=f'原始本金： {result.init_funds}'),
            html.Div(children=f'最終本金： {result.final_funds}'),
            html.Div(children=f'最終權益： {final_equity} 元'),
            html.Div(children=f'總獲利： {total_return:.0f}'),
            html.Div(children=f'總獲利(含手續費)： {total_return_with_fee:.0f}'),
            html.Div(children=f'平均天數： {avg_days:.1f} 天 (最長: {max_days:.1f} 天, 最短: {min_days:.1f}) 天'),
            html.Div(children=f'報酬率： {total_return_rate_with_fee * 100:.2f}%'),
            html.Div(children=f'年化報酬率(含手續費)： {annualized_return_rate_with_fee * 100:.2f}%'),
            dcc.Graph(figure=px.line(
                data_frame=pd.DataFrame({
                    '權益': equity_curve,
                }),
            )),
            html.Div(children=f'各倉位狀況：'),
            dash_table.DataTable(data=trades.to_dict('records'), page_size=50),
            html.Div(children=f'交易紀錄：'),
            dash_table.DataTable(data=result.trade_logs, page_size=20),
            html.Div(children=f'個股狀況：'),
            dcc.Dropdown(
                trades['stock_id'].unique(),
                id='stock_id',
            ),
            dcc.Graph(id='equity_per_stock'),
            html.Div(children=f'各倉位狀況：'),
            dash_table.DataTable(id='trades_per_stock'),
            html.Div(children=f'交易紀錄：'),
            dash_table.DataTable(id='logs_per_stock'),
        ]

        @callback(
            Output('equity_per_stock', 'figure'),
            Output('trades_per_stock', 'data'),
            Output('logs_per_stock', 'data'),
            Input('stock_id', 'value'),
        )
        def update_graph(stock_id):
            data = self.data_source[stock_id]
            stock_trades = trades[trades['stock_id'] == stock_id]

            fig_data = [
                go.Candlestick(
                    x=data.close[result.start_time:result.end_time].index,
                    open=data.open[result.start_time:result.end_time],
                    high=data.high[result.start_time:result.end_time],
                    low=data.low[result.start_time:result.end_time],
                    close=data.close[result.start_time:result.end_time],
                    increasing_line_color='red',
                    decreasing_line_color='green',
                    name='K 線',
                )
            ]

            for idx, trade in stock_trades.iterrows():
                end_date = trade['end_date']
                if not end_date:
                    end_date = result.end_time

                fig_data.append(
                    go.Scatter(
                        x=[trade['start_date'], end_date],
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

            for _, trade in stock_trades.iterrows():
                fig.add_annotation(
                    x=trade['start_date'],
                    y=trade['start_price'],
                    text="Buy",
                    arrowhead=2,
                    ax=0,
                    ay=-30
                )
                if trade['end_date']:
                    fig.add_annotation(
                        x=trade['end_date'],
                        y=trade['end_price'],
                        text="Sell",
                        arrowhead=2,
                        ax=0,
                        ay=-30
                    )

            logs = trade_logs[trade_logs['stock_id'] == stock_id]
            return fig, stock_trades.to_dict('records'), logs.to_dict('records')

        app = Dash(__name__)
        app.layout = html.Div(array)
        app.run()

    def _generate_trade_logs(self, result):
        trade_logs = pd.DataFrame(result.trade_logs, columns=[
            'idx', 'date', 'action', 'stock_id', 'shares', 'fee', 'price', 'before', 'funds', 'after', 'note',
        ])
        trade_logs = trade_logs.astype({
            'idx': 'int',
            'date': 'datetime64[ns]',
            'action': 'str',
            'stock_id': 'str',
            'shares': 'int',
            'fee': 'int',
            'price': 'float',
            'before': 'int',
            'funds': 'int',
            'after': 'int',
            'note': 'str',
        })
        return trade_logs

    def _generate_trades(self, result):
        trade_logs = self._generate_trade_logs(result)

        df = trade_logs.groupby('idx').agg(
            status=('date', lambda x: 'open' if len(x) == 1 else 'close'),
            stock_id=('stock_id', 'first'),
            shares=('shares', 'first'),
            start_date=('date', 'first'),
            end_date=('date', 'last'),
            start_price=('price', lambda x: x.iloc[0]),
            end_price=('price', lambda x: np.nan if len(x) == 1 else x.iloc[-1]),
            total_fee=('fee', 'sum'),
            note=('note', lambda x: ' | '.join(x)),
        ).reset_index()

        today_close_prices = self.data_source.close.loc[result.end_time]
        df['end_price'] = df['end_price'].fillna(df['stock_id'].map(today_close_prices))

        df['period'] = (df['end_date'] - df['start_date']).dt.days
        df['total_return'] = ((df['end_price'] - df['start_price']) * df['shares']).astype(int)
        df['total_return (fee)'] = df['total_return'] - df['total_fee']

        df['total_return_rate (fee)'] = df['total_return (fee)'] / (df['start_price'] * df['shares'])  # TODO: 考慮手續費
        df['total_return_rate (fee)'] = df['total_return_rate (fee)'].apply(lambda x: f'{x * 100:.2f}%')

        df = df[[
            'status',
            'stock_id',
            'shares',
            'start_date',
            'end_date',
            'period',
            'start_price',
            'end_price',
            'total_return',
            'total_fee',
            'total_return (fee)',
            'total_return_rate (fee)',
            'note',
        ]]

        return df

    def _calculate_equity_curve(self, result):
        equity_curve = []

        balance = result.init_funds
        trade_logs = pd.DataFrame(result.trade_logs, columns=[
            'idx', 'date', 'action', 'stock_id', 'shares', 'fee', 'price', 'before', 'funds', 'after', 'note',
        ])
        trade_logs = trade_logs.astype({
            'idx': 'int',
            'date': 'datetime64[ns]',
            'action': 'str',
            'stock_id': 'str',
            'shares': 'int',
            'fee': 'int',
            'price': 'float',
            'before': 'int',
            'funds': 'int',
            'after': 'int',
            'note': 'str',
        })

        positions = {}
        for date in self.data_source.close.loc[result.start_time:result.end_time].index:
            day_trade_logs = trade_logs[trade_logs['date'] == date]

            df = day_trade_logs[day_trade_logs['action'] == 'sell']
            for _, row in df.iterrows():
                balance += row['funds']
                del positions[row['idx']]

            df = day_trade_logs[day_trade_logs['action'] == 'buy']
            for _, row in df.iterrows():
                balance += row['funds']
                positions[row['idx']] = {
                    'stock_id': row['stock_id'],
                    'shares': row['shares'],
                }

            equity = balance

            today_close_prices = self.data_source.close.loc[date]
            for position in positions.values():
                equity += today_close_prices[position['stock_id']] * position['shares']

            equity_curve.append({
                'date': date,
                'equity': equity,
            })

        return pd.Series(
            [current_equity['equity'] for current_equity in equity_curve],
            index=[current_equity['date'] for current_equity in equity_curve],
        )
