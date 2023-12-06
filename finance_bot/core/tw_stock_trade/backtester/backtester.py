import datetime as dt
import traceback
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

import numpy as np
import pandas as pd
import rich
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    SpinnerColumn,
)

from finance_bot.core.tw_stock_trade.backtester.result import Result
from finance_bot.core.tw_stock_trade.backtester.broker import SimBroker
from finance_bot.core.tw_stock_trade.backtester.data_source.data_source import DataSource


class Backtester:
    data_class = DataSource
    broker_class = SimBroker

    def run(self, init_balance, start, end, strategies):
        start_time = dt.datetime.now()
        start = pd.Timestamp(start)
        end = pd.Timestamp(end)

        with ProcessPoolExecutor() as pool:
            parent_message_conn, message_conn = mp.Pipe()

            tasks = []
            for idx, [strategy_class, params] in enumerate(strategies):
                task = pool.submit(
                    self.backtest,
                    message_conn=message_conn,
                    result_id=idx,
                    init_balance=init_balance,
                    start=start,
                    end=end,
                    strategy_class=strategy_class,
                    params=params
                )
                tasks.append(task)

            with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold blue]{task.description}", justify="right"),
                    BarColumn(),
                    "{task.completed}/{task.total} [{task.fields[detail]}]",
                    "•",
                    "[progress.percentage]{task.percentage:>3.1f}%",
                    "•",
                    TimeRemainingColumn(),
            ) as progress:
                task_id_map = dict()
                while True:
                    message = parent_message_conn.recv()
                    if message['action'] == 'init':
                        task_id = progress.add_task(message['description'], detail='', start=False)
                        task_id_map[message['result_id']] = task_id
                    elif message['action'] == 'start':
                        progress.update(task_id_map[message['result_id']], total=message['total'])
                        progress.start_task(task_id_map[message['result_id']])
                    elif message['action'] == 'update':
                        progress.update(task_id_map[message['result_id']], advance=1, detail=message['detail'])
                    elif message['action'] == 'done':
                        del task_id_map[task_id_map[message['result_id']]]
                    elif message['action'] == 'error':
                        rich.print(message['detail'])

                    if not task_id_map:
                        break

            results = []
            for task in tasks:
                result = task.result()
                results.append(result)

        rich.print('回測花費時間：', dt.datetime.now() - start_time)
        return results

    def backtest(self, message_conn, result_id, init_balance, start, end, strategy_class, params):
        try:
            strategy = strategy_class()
            strategy.params = {
                **strategy_class.params,
                **params,
            }

            strategy_name = strategy.name
            params_output = ', '.join(f'{k}={v}' for k, v in strategy.params.items())
            message_conn.send(dict(
                result_id=result_id,
                action='init',
                description=f'{strategy_name} <{params_output}> 回測中',
            ))

            data_source = self.data_class(
                start=start,
                end=end,
                all_stock_ids=strategy_class.available_stock_ids if strategy_class.available_stock_ids else None,
            )
            broker = self.broker_class(data_source, init_balance)

            strategy.data_source = data_source
            strategy.broker = broker
            strategy.pre_handle()

            message_conn.send(dict(
                result_id=result_id,
                action='start',
                total=len(data_source.all_date_range) + 3,
            ))

            data_source.is_limit = True
            for today in data_source.all_date_range:
                message_conn.send(dict(
                    result_id=result_id,
                    action='update',
                    detail=today.strftime('%Y-%m-%d'),
                ))
                data_source.set_time(today)

                for action in strategy.actions:
                    if action['operation'] == 'buy':
                        broker.buy_market(stock_id=action['stock_id'], shares=action['shares'], note=action['note'])
                    elif action['operation'] == 'sell':
                        broker.sell_all_market(stock_id=action['stock_id'], note=action['note'])
                strategy.inter_handle()

            trade_logs = self._generate_trade_logs(broker.trade_logs)
            message_conn.send(dict(
                result_id=result_id,
                action='update',
                detail='trade_logs',
            ))

            positions = self._generate_positions(data_source, trade_logs)
            message_conn.send(dict(
                result_id=result_id,
                action='update',
                detail='positions',
            ))

            equity_curve = self._calculate_equity_curve(data_source, init_balance, trade_logs)
            message_conn.send(dict(
                result_id=result_id,
                action='update',
                detail='equity_curve',
            ))
            message_conn.send(dict(
                result_id=result_id,
                action='done',
            ))

            return Result(
                id=result_id,
                strategy_name=strategy_class.name,
                init_balance=init_balance,
                final_balance=broker.current_balance,
                start_time=start,
                end_time=end,

                trade_logs=trade_logs,
                positions=positions,
                equity_curve=equity_curve,
            )
        except:
            message_conn.send(dict(
                result_id=result_id,
                action='error',
                detail=traceback.format_exc(),
            ))

    @staticmethod
    def _generate_trade_logs(trade_logs):
        trade_logs = pd.DataFrame(trade_logs, columns=[
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

    def _generate_positions(self, data_source, trade_logs):
        df = trade_logs.groupby('idx').agg(
            status=('date', lambda x: 'open' if len(x) == 1 else 'close'),
            stock_id=('stock_id', 'first'),
            shares=('shares', 'first'),
            start_date=('date', 'first'),
            end_date=('date', lambda x: None if len(x) == 1 else x.iloc[-1]),
            start_price=('price', lambda x: x.iloc[0]),
            end_price=('price', lambda x: np.nan if len(x) == 1 else x.iloc[-1]),
            total_fee=('fee', 'sum'),
            note=('note', lambda x: ' | '.join(x)),
        ).reset_index()

        today_close_prices = data_source.close.loc[data_source.end_time]
        df['end_price'] = df['end_price'].fillna(df['stock_id'].map(today_close_prices))
        df['end_date'] = df['end_date'].fillna(data_source.end_time)

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

    @staticmethod
    def _calculate_equity_curve(data_source, init_balance, trade_logs):
        equity_curve = []

        balance = init_balance
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
        for date in data_source.close.loc[data_source.start_time:data_source.end_time].index:
            day_trade_logs = trade_logs[trade_logs['date'] == date]

            df = day_trade_logs[day_trade_logs['action'] == 'buy']
            for _, row in df.iterrows():
                balance += row['funds']
                positions[row['idx']] = {
                    'stock_id': row['stock_id'],
                    'shares': row['shares'],
                }

            df = day_trade_logs[day_trade_logs['action'] == 'sell']
            for _, row in df.iterrows():
                balance += row['funds']
                del positions[row['idx']]

            equity = balance

            today_close_prices = data_source.close.loc[date]
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
