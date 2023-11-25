import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import uvicorn
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
from dash.exceptions import PreventUpdate
from fastapi import FastAPI
from rich.console import Console
from rich.table import Table
from starlette.middleware.wsgi import WSGIMiddleware

from tool.backtester.backtester.result import Result
from tool.backtester.data_source import DataSource


class Reporter:
    data_class = DataSource

    def __init__(self, results: [Result]):
        self.data_source = self.data_class()
        self.results = results

    def summary(self):
        console = Console()

        start_time = self.results[0].start_time.strftime('%Y-%m-%d')
        end_time = self.results[0].end_time.strftime('%Y-%m-%d')
        console.print('回測時間：', start_time, '~', end_time)

        init_funds = self.results[0].init_funds
        console.print('原始本金：', init_funds)

        table = Table()
        table.add_column('ID')
        table.add_column('策略')
        table.add_column('最終本金')
        table.add_column('最終權益')
        table.add_column('總獲利(含手續費)')
        table.add_column('平均天數')
        table.add_column('最短天數')
        table.add_column('最長天數')
        table.add_column('總報酬率')
        table.add_column('年化報酬率(含手續費)')

        for result in self.results:
            table.add_row(
                str(result.id),
                result.strategy_name,
                f'{result.final_funds} 元',
                f'{result.final_equity} 元',
                f'{result.total_return_with_fee} 元',
                f'{result.avg_days:.1f} 天',
                f'{result.min_days:.1f} 天',
                f'{result.max_days:.1f} 天',
                f'{result.total_return_rate_with_fee * 100:.2f}%',
                f'{result.annualized_return_rate_with_fee * 100:.2f}%',
            )

        console.print(table)

    def serve(self):
        start_time = self.results[0].start_time.strftime('%Y-%m-%d')
        end_time = self.results[0].end_time.strftime('%Y-%m-%d')
        init_funds = self.results[0].init_funds

        array = [
            html.Header(children='績效報告', style={'fontSize': '2em', 'fontWeight': '800'}),
            html.Div(children=f'回測時間： {start_time} ~ {end_time}'),
            html.Div(children=f'原始本金： {init_funds}'),
        ]

        result_summaries = [
            {
                'ID': result.id,
                '策略': result.strategy_name,
                '最終本金': f'{result.final_funds} 元',
                '最終權益': f'{result.final_equity} 元',
                '總獲利(含手續費)': f'{result.total_return_with_fee} 元',
                '平均天數': f'{result.avg_days:.1f} 天',
                '最短天數': f'{result.min_days:.1f} 天',
                '最長天數': f'{result.max_days:.1f} 天',
                '總報酬率': f'{result.total_return_rate_with_fee * 100:.2f}%',
                '年化報酬率(含手續費)': f'{result.annualized_return_rate_with_fee * 100:.2f}%',
            } for result in self.results
        ]
        array.append(
            dash_table.DataTable(data=result_summaries, page_size=20),
        )

        result_ids = [result.id for result in self.results]
        array.extend([
            html.Header(children=f'選擇策略：', style={'fontSize': '1.5em', 'fontWeight': '600'}),
            dcc.Dropdown(id='result_id', options=result_ids, value=result_ids[0]),
            dash_table.DataTable(id='summary'),
            dcc.Graph(id='equity_curve'),
            html.Div(children=f'倉位狀態：'),
            dash_table.DataTable(id='positions', page_size=50),
            html.Div(children=f'交易紀錄：'),
            dash_table.DataTable(id='trade_logs', page_size=50),
            html.Header(children=f'個股狀況：', style={'fontSize': '1.5em', 'fontWeight': '600'}),
            dcc.Dropdown(id='stock_id'),
        ])

        result_map = {result.id: result for result in self.results}
        result_summary_map = {
            summary['ID']: summary for summary in result_summaries
        }

        @callback(
            Output('summary', 'data'),
            Output('equity_curve', 'figure'),
            Output('positions', 'data'),
            Output('trade_logs', 'data'),
            Output('stock_id', 'options'),
            Output('stock_id', 'value'),
            Input('result_id', 'value'),
        )
        def update_strategy(result_id):
            result = result_map[result_id]
            stock_ids = result.positions['stock_id'].unique()

            return (
                [result_summary_map[result_id]],
                px.line(
                    data_frame=pd.DataFrame({
                        '權益': result.equity_curve,
                    }),
                ),
                result.positions.to_dict('records'),
                result.trade_logs.to_dict('records'),
                stock_ids,
                stock_ids[0],
            )

        array.extend([
            dcc.Graph(id='equity_per_stock'),
            html.Div(children=f'各倉位狀況：'),
            dash_table.DataTable(id='positions_per_stock'),
            html.Div(children=f'交易紀錄：'),
            dash_table.DataTable(id='trade_logs_per_stock'),
        ])

        @callback(
            Output('equity_per_stock', 'figure'),
            Output('positions_per_stock', 'data'),
            Output('trade_logs_per_stock', 'data'),
            Input('stock_id', 'value'),
            State('result_id', 'value')
        )
        def update_graph(stock_id, result_id):
            result = result_map[result_id]

            data = self.data_source[stock_id]
            positions_per_stock = result.positions[result.positions['stock_id'] == stock_id]

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

            for idx, position in positions_per_stock.iterrows():
                end_date = position['end_date']
                if not end_date:
                    end_date = result.end_time

                fig_data.append(
                    go.Scatter(
                        x=[position['start_date'], end_date],
                        y=[position['start_price'], position['end_price']],
                        line_color='red' if position['total_return'] > 0 else 'green',
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

            for _, position in positions_per_stock.iterrows():
                fig.add_annotation(
                    x=position['start_date'],
                    y=position['start_price'],
                    text="Buy",
                    arrowhead=2,
                    ax=0,
                    ay=-30
                )
                if position['end_date']:
                    fig.add_annotation(
                        x=position['end_date'],
                        y=position['end_price'],
                        text="Sell",
                        arrowhead=2,
                        ax=0,
                        ay=-30
                    )

            trade_logs_per_stock = result.trade_logs[result.trade_logs['stock_id'] == stock_id]
            return (
                fig,
                positions_per_stock.to_dict('records'),
                trade_logs_per_stock.to_dict('records'),
            )

        app = Dash(__name__)
        app.layout = html.Div(array)

        server = FastAPI()
        server.mount("/", WSGIMiddleware(app.server))
        uvicorn.run(server, port=8050, access_log=False)
