import abc
import math

import pandas as pd

from finance_bot.core.tw_stock_trade.broker import BrokerBase
from finance_bot.core.tw_stock_trade.market_data import MarketData


class StrategyBase(abc.ABC):
    name: str
    params: dict = {}

    stock_id: str
    broker: BrokerBase
    market_data: MarketData
    preload_days = 10

    _indicators = {}
    _actions = []
    _day_cache = set()

    def init(self, all_data):
        return {}

    @abc.abstractmethod
    def handle(self):
        pass

    def new_target_list(self, conditions, *, available_list=None):
        for idx, condition in enumerate(conditions):
            if not isinstance(condition, pd.Series):
                raise ValueError(f'Condition {idx} is invalid')

        if available_list is not None:
            conditions.append(
                pd.Series([True] * len(available_list), index=available_list)
            )

        # 將所有 bool series 結合成 dataframe
        df = pd.concat(conditions, axis=1)
        # 補上 na
        df = df.fillna(False)
        # 用 all 整合成 series
        s = df.all(axis=1)
        return s[s].index.tolist()

    def buy_next_day_market(self, stock_id, note=''):
        """
        在隔天市價買入 (但在回測試會以買在最高價計算)
        """
        # 一張股票一天只會操作一次
        if stock_id in self._day_cache:
            return

        invested_funds = self.broker.invested_funds
        current_balance = self.broker.current_balance
        max_single_position_exposure = self.params.get('max_single_position_exposure', 0.1)
        single_entry_limit = min(math.floor((invested_funds + current_balance) * max_single_position_exposure),
                                 current_balance)
        entry_price = self.data.get_stock_close_price(stock_id)
        shares = int((single_entry_limit / (entry_price * (1 + self.broker.commission_info.fee_rate)) // 1000) * 1000)

        if shares < 1000:
            return

        self._actions.append({
            'operation': 'buy',
            'stock_id': stock_id,
            'shares': shares,
            'note': note,
        })

        self._day_cache.add(stock_id)

    def sell_next_day_market(self, stock_id, note=''):
        """
        在隔天市價賣出 (但在回測時會以賣在最低價計算)
        :return:
        """
        # 一張股票一天只會操作一次
        if stock_id in self._day_cache:
            return

        self._actions.append({
            'operation': 'sell',
            'stock_id': stock_id,
            'note': note,
        })

        self._day_cache.add(stock_id)

    @property
    def actions(self):
        return self._actions

    @property
    def data(self):
        return self.market_data

    @property
    def close(self):
        return self.data.close.iloc[-1]

    @property
    def holding_close(self):
        return self.close[self.broker.holding_stock_ids]

    @property
    def volume(self):
        return self.data.volume.iloc[-1]

    @property
    def today(self):
        return self.market_data.current_time

    @property
    def current_shares(self):
        return self.broker.holding_stock_shares_s.reindex(self.close.index, fill_value=0)

    @property
    def entry_date(self):
        return self.broker.holding_stock_entry_date_s

    @property
    def entry_price(self):
        return self.broker.holding_stock_entry_price_s

    @property
    def break_even_price(self):
        return self.broker.holding_stock_break_even_price_s

    @property
    def profit_with_fee(self):
        return self.holding_close - self.break_even_price

    @property
    def growth_rate(self):
        return (self.holding_close - self.entry_price) / self.entry_price

    @property
    def max_growth_rate(self):
        close = self.data.close[self.entry_date.index]
        data = []
        for stock_id in close.columns:
            max_close = close.loc[self.entry_date[stock_id]:, stock_id].max()
            entry_price = self.entry_price[stock_id]
            data.append(dict(
                stock_id=stock_id,
                max_growth_rate=(max_close - entry_price) / entry_price
            ))

        return pd.DataFrame(data, columns=['stock_id', 'max_growth_rate']).set_index('stock_id')['max_growth_rate']

    @property
    def has_profit(self):
        return self.profit_with_fee > 0

    @property
    def max_profit_rate(self):
        return (self.break_even_price - self.entry_price) / self.entry_price

    def pre_handle(self):
        self._indicators = self.init(self.data)

    def i(self, key):
        return self._indicators[key].loc[:self.today]

    def inter_handle(self):
        # 一定時間範圍內不做任何事以確保策略能正常運行（如讀取前一天的資料）
        if (self.market_data.current_time - self.market_data.start_time).days < self.preload_days:
            return

        self._day_cache = set()
        self._actions = []
        self.handle()
