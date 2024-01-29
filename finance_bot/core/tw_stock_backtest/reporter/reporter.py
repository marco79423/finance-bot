import plotly.graph_objects as go
import plotly.subplots as sp
import uvicorn
from a2wsgi import WSGIMiddleware
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
from fastapi import FastAPI
from rich.console import Console
from rich.table import Table

from finance_bot.core.tw_stock_backtest.result import Result
from finance_bot.core.data_sync.tw_stock.market_data import MarketData


class Reporter:
    data_class = MarketData

    def __init__(self, results: [Result]):
        self.market_data = self.data_class()
        self.results = results

    def summary(self):
        console = Console()

        start_time = self.results[0].start_time.strftime('%Y-%m-%d')
        end_time = self.results[0].end_time.strftime('%Y-%m-%d')
        console.print('回測時間：', start_time, '~', end_time)

        init_balance = self.results[0].init_balance
        console.print('原始本金：', init_balance)

        table = Table()
        table.add_column('策略')
        table.add_column('參數')
        table.add_column('最終權益')
        table.add_column('總獲利(含手續費)')
        table.add_column('手續費')
        table.add_column('平均天數')
        table.add_column('最長天數')
        table.add_column('勝率')
        table.add_column('MDD')
        table.add_column('總報酬率')
        table.add_column('年化報酬率(含手續費)')

        for result in self.results:
            table.add_row(
                result.strategy_name,
                result.params_key,
                f'{result.final_equity} 元',
                f'{result.total_return} 元',
                f'{result.total_return - result.total_return_with_fee} 元',
                f'{result.avg_days:.1f} 天',
                f'{result.max_days:.1f} 天',
                f'{result.win_rate * 100:.2f}%',
                f'{result.maximum_drawdown * 100:.2f}%',
                f'{result.total_return_rate_with_fee * 100:.2f}%',
                f'{result.annualized_return_rate_with_fee * 100:.2f}%',
            )

        console.print(table)

    def serve(self):
        start_time = self.results[0].start_time.strftime('%Y-%m-%d')
        end_time = self.results[0].end_time.strftime('%Y-%m-%d')
        init_funds = self.results[0].init_balance

        array = [
            html.Header(children='績效報告', style={'fontSize': '2em', 'fontWeight': '800'}),
            html.Div(children=f'回測時間： {start_time} ~ {end_time}'),
            html.Div(children=f'原始本金： {init_funds}'),
        ]

        result_summaries = [
            {
                'ID': str(result.id),
                '策略': result.strategy_name,
                '參數': result.params_key,
                '最終本金': f'{result.final_balance} 元',
                '最終權益': f'{result.final_equity} 元',
                '總獲利(含手續費)': f'{result.total_return_with_fee} 元',
                '手續費': f'{result.total_return - result.total_return_with_fee} 元',
                '平均天數': f'{result.avg_days:.1f} 天',
                '最短天數': f'{result.min_days:.1f} 天',
                '最長天數': f'{result.max_days:.1f} 天',
                '勝率': f'{result.win_rate * 100:.2f}%',
                'MDD': f'{result.maximum_drawdown * 100:.2f}%',
                '總報酬率': f'{result.total_return_rate_with_fee * 100:.2f}%',
                '年化報酬率(含手續費)': f'{result.annualized_return_rate_with_fee * 100:.2f}%',
            } for result in self.results
        ]
        array.append(
            dash_table.DataTable(data=result_summaries, page_size=20, sort_action='native', sort_mode='multi'),
        )

        # Dash 似乎不能正常顯示 long int
        result_ids = [str(result.id) for result in self.results]
        array.extend([
            html.Header(children=f'選擇策略：', style={'fontSize': '1.5em', 'fontWeight': '600'}),
            dcc.Dropdown(id='result_id', options=result_ids, value=result_ids[0]),
            dash_table.DataTable(id='summary', sort_action='native', sort_mode='multi'),
            html.Div(children=f'權益曲線：'),
            dcc.Graph(id='equity_curve'),
            html.Div(children=f'倉位狀態：'),
            dash_table.DataTable(id='positions', sort_action='native', sort_mode='multi', page_size=50),
            html.Div(children=f'交易紀錄：'),
            dash_table.DataTable(id='trade_logs', sort_action='native', sort_mode='multi', page_size=50),
            html.Header(children=f'個股狀況：', style={'fontSize': '1.5em', 'fontWeight': '600'}),
            dcc.Dropdown(id='stock_id'),
        ])

        result_map = {str(result.id): result for result in self.results}
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
            stock_ids = sorted(result.positions_df['stock_id'].unique())

            fig = sp.make_subplots(
                rows=2,
                cols=1,
                vertical_spacing=0.1,
                subplot_titles=('權益', '持倉股票'),
                row_heights=[0.5, 0.5],
                shared_xaxes=True,
            )

            trace = go.Scatter(
                x=result.equity_curve_s.index,
                y=result.equity_curve_s,
                name=f'權益'
            )
            fig.add_trace(trace, row=1, col=1)

            trace = go.Scatter(
                x=result.stock_count_s.index,
                y=result.stock_count_s,
                name=f'權益'
            )
            fig.add_trace(trace, row=2, col=1)

            fig.update_layout(
                height=600,
                xaxis1_rangeslider_visible=False,
                xaxis1_visible=False,  # fig.update_xaxes(visible=False, row=1, col=1)
            )

            return (
                [result_summary_map[result_id]],
                fig,
                result.positions_df.to_dict('records'),
                result.trade_logs_df.to_dict('records'),
                stock_ids,
                stock_ids[0],
            )

        array.extend([
            dcc.Graph(id='equity_per_stock'),
            html.Div(children=f'各倉位狀況：'),
            dash_table.DataTable(id='positions_per_stock', sort_action='native', sort_mode='multi'),
            html.Div(children=f'交易紀錄：'),
            dash_table.DataTable(id='trade_logs_per_stock', sort_action='native', sort_mode='multi'),
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

            data = self.market_data[stock_id]
            positions_per_stock = result.positions_df[result.positions_df['stock_id'] == stock_id]

            fig = sp.make_subplots(
                rows=2,
                cols=1,
                vertical_spacing=0.1,
                subplot_titles=('K 線', '成交量'),
                row_heights=[0.8, 0.2],
                shared_xaxes=True,
            )

            trace1 = go.Candlestick(
                x=data.close[result.start_time:result.end_time].index,
                open=data.open[result.start_time:result.end_time],
                high=data.high[result.start_time:result.end_time],
                low=data.low[result.start_time:result.end_time],
                close=data.close[result.start_time:result.end_time],
                increasing_line_color='red',
                decreasing_line_color='green',
                name='K 線',
            )
            fig.add_trace(trace1, row=1, col=1)

            trace2 = go.Bar(
                x=data.close[result.start_time:result.end_time].index,
                y=data.volume[result.start_time:result.end_time],
                name='成交量',
            )
            fig.add_trace(trace2, row=2, col=1)

            for idx, position in positions_per_stock.iterrows():
                end_date = position['end_date']
                trace = go.Scatter(
                    x=[position['start_date'], end_date],
                    y=[position['start_price'], position['end_price']],
                    line_color='red' if position['total_return'] > 0 else 'green',
                    name=f'trade {idx}'
                )
                fig.add_trace(trace, row=1, col=1)

            for _, position in positions_per_stock.iterrows():
                fig.add_annotation(
                    xref='x',
                    yref='y',
                    x=position['start_date'],
                    y=position['start_price'],
                    text="Buy",
                    arrowhead=2,
                    ax=0,
                    ay=-30
                )
                if position['end_date']:
                    fig.add_annotation(
                        xref='x',
                        yref='y',
                        x=position['end_date'],
                        y=position['end_price'],
                        text="Sell",
                        arrowhead=2,
                        ax=0,
                        ay=-30
                    )

            fig.update_layout(
                height=600,
                xaxis1_rangeslider_visible=False,
                xaxis1_visible=False,  # fig.update_xaxes(visible=False, row=1, col=1)
            )

            trade_logs_per_stock = result.trade_logs_df[result.trade_logs_df['stock_id'] == stock_id]
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
