import datetime as dt
import multiprocessing as mp
import traceback
from concurrent.futures import ProcessPoolExecutor

import pandas as pd
import rich
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    SpinnerColumn,
)

from finance_bot.core.tw_stock_trade.backtester.limited_market_data import LimitedMarketData
from finance_bot.core.tw_stock_trade.backtester.result import Result
from finance_bot.core.tw_stock_trade.backtester.sim_broker import SimBroker
from finance_bot.core.tw_stock_trade.market_data import MarketData


class Backtester:
    data_class = MarketData
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
            params_key = ', '.join(f'{k}={strategy.params[k]}' for k in sorted(strategy.params))
            message_conn.send(dict(
                result_id=result_id,
                action='init',
                description=f'{strategy_name} <{params_key}> 回測中',
            ))

            market_data = self.data_class()
            limited_market_data = LimitedMarketData(
                market_data=market_data,
                start=start,
                end=end,
            )
            broker = self.broker_class(limited_market_data, init_balance)

            strategy.market_data = limited_market_data
            strategy.broker = broker
            strategy.pre_handle()

            message_conn.send(dict(
                result_id=result_id,
                action='start',
                total=len(limited_market_data.all_date_range),
            ))

            limited_market_data.is_limit = True
            for today in limited_market_data.all_date_range:
                message_conn.send(dict(
                    result_id=result_id,
                    action='update',
                    detail=today.strftime('%Y-%m-%d'),
                ))
                limited_market_data.set_current_time(today)

                for action in strategy.actions:
                    if action['operation'] == 'buy':
                        broker.buy_market(stock_id=action['stock_id'], shares=action['shares'], note=action['note'])
                    elif action['operation'] == 'sell':
                        broker.sell_all_market(stock_id=action['stock_id'], note=action['note'])

                broker.refresh()
                strategy.inter_handle()

            message_conn.send(dict(
                result_id=result_id,
                action='done',
            ))

            return Result(
                id=result_id,
                strategy_name=strategy_class.name,
                params_key=params_key,
                init_balance=init_balance,
                final_balance=broker.current_balance,
                start_time=start,
                end_time=end,
                trade_logs=broker.trade_logs,
                market_data=market_data,
            )
        except:
            message_conn.send(dict(
                result_id=result_id,
                action='error',
                detail=traceback.format_exc(),
            ))
