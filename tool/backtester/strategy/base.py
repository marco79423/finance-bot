import abc
from typing import Optional, List

import pandas as pd

from tool.backtester.broker import Broker
from tool.backtester.data_source import StockDataSource


class StrategyBase(abc.ABC):
    name: str
    params: dict = {}

    stock_id: str
    broker: Broker
    data_source: StockDataSource
    preload_days = 10

    available_stock_ids: Optional[List[str]] = None

    _indicators = {}
    _actions = []

    def init(self, all_data):
        return {}

    @abc.abstractmethod
    def handle(self):
        pass

    def new_target_list(self, conditions):
        df = pd.Series([True] * len(self.close.index), index=self.close.index)
        for condition in conditions:
            df = df & condition
        return df.index.tolist()

    def buy_next_day_market(self, stock_id, note=''):
        """
        在隔天市價買入 (但在回測試會以買在最高價計算)
        """
        self._actions.append({
            'operation': 'buy',
            'stock_id': stock_id,
            'note': note,
        })

    def sell_next_day_market(self, stock_id, note=''):
        """
        在隔天市價賣出 (但在回測時會以賣在最低價計算)
        :return:
        """
        self._actions.append({
            'operation': 'sell',
            'stock_id': stock_id,
            'note': note,
        })

    @property
    def actions(self):
        return self._actions

    @property
    def data(self):
        return self.data_source

    @property
    def close(self):
        return self.data.close.iloc[-1]

    @property
    def volume(self):
        return self.data.volume.iloc[-1]

    @property
    def today(self):
        return self.data_source.current_time

    @property
    def current_shares(self):
        return self.broker.current_shares.reindex(self.close.index, fill_value=0)

    @property
    def entry_date(self):
        return self.broker.entry_date

    @property
    def entry_price(self):
        return self.broker.entry_price

    @property
    def break_even_price(self):
        return self.broker.break_even_price

    @property
    def has_profit(self):
        return self.close.loc[self.broker.break_even_price.index] > self.break_even_price

    def pre_handle(self):
        self._indicators = self.init(self.data)

    def i(self, key):
        return self._indicators[key].loc[:self.today]

    def inter_handle(self):
        # 一定時間範圍內不做任何事以確保策略能正常運行（如讀取前一天的資料）
        if (self.data_source.current_time - self.data_source.start_time).days < self.preload_days:
            return

        self._actions = []
        self.handle()
