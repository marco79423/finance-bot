import datetime as dt
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    SpinnerColumn,
)

from tool.backtester.backtester.result import Result
from tool.backtester.broker import Broker
from tool.backtester.data_source.stock_data_source import StockDataSource


class Backtester:
    data_class = StockDataSource
    broker_class = Broker

    def run(self, init_funds, start, end, strategies):
        start_time = dt.datetime.now()
        start = pd.Timestamp(start)
        end = pd.Timestamp(end)

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
            with ThreadPoolExecutor() as pool:
                tasks = []
                for idx, [strategy_class, params] in enumerate(strategies):
                    task = pool.submit(
                        self.backtest,
                        result_id=idx,
                        progress=progress,
                        init_funds=init_funds,
                        start=start,
                        end=end,
                        strategy_class=strategy_class,
                        max_single_position_exposure=params['max_single_position_exposure']
                    )
                    tasks.append(task)

                results = []
                for task in tasks:
                    result = task.result()
                    results.append(result)

        console = Console()
        console.print('回測花費時間：', dt.datetime.now() - start_time)
        return results

    def backtest(self, result_id, progress, init_funds, start, end, strategy_class, max_single_position_exposure):
        strategy_name = strategy_class.name

        task_id = progress.add_task(
            f'{strategy_name}[max_single_position_exposure={max_single_position_exposure}] 回測中', detail='',
            start=False)
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

        progress.update(task_id, total=len(data_source.all_date_range) + 3)
        progress.start_task(task_id)
        for today in data_source.all_date_range:
            progress.update(task_id, advance=1, detail=today.strftime('%Y-%m-%d'))
            data_source.set_time(today)

            for action in strategy.actions:
                if action['operation'] == 'buy':
                    broker.buy(stock_id=action['stock_id'], note=action['note'])
                elif action['operation'] == 'sell':
                    broker.sell(stock_id=action['stock_id'], note=action['note'])
            strategy.inter_handle()

        trade_logs = self._generate_trade_logs(broker.trade_logs)
        progress.update(task_id, advance=1, detail='trade_logs')

        positions = self._generate_positions(data_source, trade_logs)
        progress.update(task_id, advance=1, detail='positions')

        equity_curve = self._calculate_equity_curve(data_source, init_funds, trade_logs)
        progress.update(task_id, advance=1, detail='equity_curve')

        return Result(
            id=result_id,
            strategy_name=strategy_class.name,
            max_single_position_exposure=max_single_position_exposure,
            init_funds=init_funds,
            final_funds=broker.funds,
            start_time=start,
            end_time=end,

            trade_logs=trade_logs,
            positions=positions,
            equity_curve=equity_curve,
        )

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
            end_date=('date', 'last'),
            start_price=('price', lambda x: x.iloc[0]),
            end_price=('price', lambda x: np.nan if len(x) == 1 else x.iloc[-1]),
            total_fee=('fee', 'sum'),
            note=('note', lambda x: ' | '.join(x)),
        ).reset_index()

        today_close_prices = data_source.close.loc[data_source.end_time]
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

    @staticmethod
    def _calculate_equity_curve(data_source, init_funds, trade_logs):
        equity_curve = []

        balance = init_funds
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
