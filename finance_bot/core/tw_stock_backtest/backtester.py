import datetime as dt
import hashlib
import json
import multiprocessing as mp
import time
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
from sqlalchemy import select
from sqlalchemy.orm import Session

from finance_bot.core.tw_stock_backtest.limited_market_data import LimitedMarketData
from finance_bot.core.tw_stock_backtest.result import Result
from finance_bot.core.tw_stock_backtest.sim_broker import SimBroker
from finance_bot.core.tw_stock_data_sync.market_data import MarketData
from finance_bot.infrastructure import infra
from finance_bot.model.tw_stock_backtest_result import TWStockBacktestResult
from finance_bot.utility import generate_id


class Backtester:
    data_class = MarketData
    broker_class = SimBroker

    def __init__(self):
        self.market_data = self.data_class()

    def run_task(self, init_balance, start, end, strategy_class, params):
        start = pd.Timestamp(start)
        end = pd.Timestamp(end)

        strategy = strategy_class()
        strategy.params = {
            **strategy.params,
            **params,
        }
        signature = self._generate_signature(strategy, init_balance, start, end)

        # if not strategy.stabled:
        #     return

        with Session(infra.db.engine) as session:
            tw_stock_backtest_result = session.scalar(
                select(TWStockBacktestResult)
                .where(TWStockBacktestResult.signature == signature)
                .limit(1)
            )
            if tw_stock_backtest_result:
                return

        result_id = generate_id()
        limited_market_data = LimitedMarketData(
            market_data=self.market_data,
            start=start,
            end=end,
        )
        broker = self.broker_class(limited_market_data, init_balance)

        strategy.market_data = limited_market_data
        strategy.broker = broker
        strategy.pre_handle()

        limited_market_data.is_limit = True
        for today in limited_market_data.all_date_range:
            limited_market_data.set_current_time(today)

            for action in strategy.actions:
                if action['operation'] == 'buy':
                    broker.buy_market(stock_id=action['stock_id'], shares=action['shares'], note=action['note'])
                elif action['operation'] == 'sell':
                    broker.sell_all_market(stock_id=action['stock_id'], note=action['note'])

            broker.refresh()
            strategy.inter_handle()

        with Session(infra.db.engine) as session:
            infra.db.sync_insert_or_update(session, TWStockBacktestResult, dict(
                id=result_id,
                signature=signature,
                strategy_name=strategy.name,
                params=json.dumps(params),
                init_balance=init_balance,
                final_balance=broker.current_balance,
                start_time=start.to_pydatetime(),
                end_time=end.to_pydatetime(),
                trade_logs=json.dumps(broker.trade_logs),
            ))

    def run(self, init_balance, start, end, strategy_configs):
        start_time = dt.datetime.now()
        start = pd.Timestamp(start)
        end = pd.Timestamp(end)

        with ProcessPoolExecutor() as pool:
            parent_message_conn, message_conn = mp.Pipe()

            tasks = []
            for [strategy_class, params] in strategy_configs:
                task = pool.submit(
                    self.backtest,
                    message_conn=message_conn,
                    market_data=self.market_data,
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
                        del task_id_map[message['result_id']]
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

    def backtest(self, message_conn, market_data, init_balance, start, end, strategy_class, params):
        strategy = strategy_class()
        strategy.params = {
            **strategy.params,
            **params,
        }
        signature = self._generate_signature(strategy, init_balance, start, end)

        if strategy.stabled:
            with Session(infra.db.engine) as session:
                tw_stock_backtest_result = session.scalar(
                    select(TWStockBacktestResult)
                    .where(TWStockBacktestResult.signature == signature)
                    .limit(1)
                )

            if tw_stock_backtest_result:
                result_id = tw_stock_backtest_result.id
                message_conn.send(dict(
                    result_id=result_id,
                    action='init',
                    description=f'{strategy.name} <{result_id}> 回測中',
                ))

                message_conn.send(dict(
                    result_id=result_id,
                    action='start',
                    total=1,
                ))

                message_conn.send(dict(
                    result_id=result_id,
                    action='update',
                    detail='讀取快取',
                ))

                time.sleep(1)
                trade_logs = json.loads(tw_stock_backtest_result.trade_logs)
                params = json.loads(tw_stock_backtest_result.params)

                message_conn.send(dict(
                    result_id=result_id,
                    action='done',
                ))

                return Result(
                    id=result_id,
                    strategy_name=strategy_class.name,
                    params=params,
                    init_balance=init_balance,
                    final_balance=tw_stock_backtest_result.final_balance,
                    start_time=start,
                    end_time=end,
                    trade_logs=trade_logs,
                    market_data=market_data,
                )

        result_id = generate_id()
        message_conn.send(dict(
            result_id=result_id,
            action='init',
            description=f'{strategy.name} <{result_id}> 回測中',
        ))

        limited_market_data = LimitedMarketData(
            market_data=market_data,
            start=start,
            end=end,
        )
        broker = self.broker_class(limited_market_data, init_balance)

        strategy.market_data = limited_market_data
        strategy.broker = broker

        message_conn.send(dict(
            result_id=result_id,
            action='start',
            total=len(limited_market_data.all_date_range),
        ))

        try:
            strategy.pre_handle()

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

            if strategy.stabled:
                with Session(infra.db.engine) as session:
                    infra.db.sync_insert_or_update(session, TWStockBacktestResult, dict(
                        id=result_id,
                        signature=signature,
                        strategy_name=strategy.name,
                        params=json.dumps(params),
                        init_balance=init_balance,
                        final_balance=broker.current_balance,
                        start_time=start.to_pydatetime(),
                        end_time=end.to_pydatetime(),
                        trade_logs=json.dumps(broker.trade_logs),
                    ))

            message_conn.send(dict(
                result_id=result_id,
                action='done',
            ))

            return Result(
                id=result_id,
                strategy_name=strategy.name,
                params=params,
                init_balance=init_balance,
                final_balance=broker.current_balance,
                start_time=start,
                end_time=end,
                trade_logs=broker.trade_logs,
                market_data=market_data,
            )

        except Exception as e:
            message_conn.send(dict(
                result_id=result_id,
                action='error',
                detail=traceback.format_exc(),
            ))

    @staticmethod
    def _generate_signature(strategy, init_balance, start, end):
        m = hashlib.md5()
        m.update(strategy.name.encode())
        m.update(', '.join(f'{k}={strategy.params[k]}' for k in sorted(strategy.params)).encode())
        m.update(str(init_balance).encode())
        m.update(start.isoformat().encode())
        m.update(end.isoformat().encode())
        key = m.hexdigest()
        return key
