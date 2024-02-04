import abc
import math
from types import FunctionType

import pandas as pd

from finance_bot.core.tw_stock_data_sync.market_data import MarketDataBase
from finance_bot.core.tw_stock_trade.broker import BrokerBase
from finance_bot.utility import Cache


class StrategyBase(abc.ABC):
    name: str
    params: dict = {}
    stabled: bool = False

    broker: BrokerBase
    market_data: MarketDataBase
    preload_days = 10

    _indicators = {}
    _actions = []
    _day_action_cache = set()
    _data_cache = Cache()

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
        if stock_id in self._day_action_cache:
            return

        invested_funds = self.broker.invested_funds
        current_balance = self.broker.current_balance
        max_single_position_exposure = self.params.get('max_single_position_exposure', 0.1)
        single_entry_limit = min(math.floor((invested_funds + current_balance) * max_single_position_exposure),
                                 current_balance)
        price = self.data.get_stock_close_price(stock_id)
        shares = int((single_entry_limit / (price * (1 + self.broker.commission_info.fee_rate)) // 1000) * 1000)
        total = int(price * shares) + self.broker.commission_info.get_buy_commission(price, shares)

        if shares < 1000:
            return

        self._actions.append({
            'operation': 'buy',
            'stock_id': stock_id,
            'shares': int(shares),
            'price': float(price),
            'total': total,
            'note': note,
        })

        self._day_action_cache.add(stock_id)

    def sell_next_day_market(self, stock_id, note=''):
        """
        在隔天市價賣出 (但在回測時會以賣在最低價計算)
        :return:
        """
        # 一張股票一天只會操作一次
        if stock_id in self._day_action_cache:
            return

        shares = self.broker.holding_stock_shares_s.loc[stock_id]
        price = self.data.get_stock_close_price(stock_id)
        total = int(price * shares) - self.broker.commission_info.get_sell_commission(price, shares)

        self._actions.append({
            'operation': 'sell',
            'stock_id': stock_id,
            'shares': int(shares),
            'price': float(price),
            'total': total,
            'note': note,
        })

        self._day_action_cache.add(stock_id)

    @property
    def actions(self):
        return self._actions

    @property
    def data(self):
        return self.market_data

    @property
    def open(self):
        return self._data_cache.get('open', lambda: self.data.open.iloc[-1])

    @property
    def close(self):
        return self._data_cache.get('close', lambda: self.data.close.iloc[-1])

    @property
    def holding_close(self):
        return self._data_cache.get('holding_close', lambda: self.close[self.broker.holding_stock_ids])

    @property
    def volume(self):
        return self._data_cache.get('volume', lambda: self.data.volume.iloc[-1])

    @property
    def monthly_revenue(self):
        return self._data_cache.get('monthly_revenue', lambda: self.data.monthly_revenue.iloc[-1])

    @property
    def today(self):
        return self.market_data.current_time

    @property
    def current_shares(self):
        return self._data_cache.get('current_shares',
                                    lambda: self.broker.holding_stock_shares_s.reindex(self.close.index, fill_value=0))

    @property
    def entry_date(self):
        return self.broker.holding_stock_entry_date_s

    @property
    def avg_price(self):
        return self.broker.holding_stock_avg_price_s

    @property
    def break_even_price(self):
        return self.broker.holding_stock_break_even_price_s

    @property
    def profit_with_fee(self):
        return self._data_cache.get('profit_with_fee', lambda: self.holding_close - self.break_even_price)

    @property
    def growth_rate(self):
        return self._data_cache.get('growth_rate', lambda: (self.holding_close - self.avg_price) / self.avg_price)

    @property
    def max_growth_rate(self):
        def calc_max_growth_rate():
            close = self.data.close[self.entry_date.index]
            data = []
            for stock_id in close.columns:
                max_close = close.loc[self.entry_date[stock_id]:, stock_id].max()
                entry_price = self.avg_price[stock_id]
                data.append(dict(
                    stock_id=stock_id,
                    max_growth_rate=(max_close - entry_price) / entry_price
                ))
            return pd.DataFrame(data, columns=['stock_id', 'max_growth_rate']).set_index('stock_id')['max_growth_rate']

        return self._data_cache.get('max_growth_rate', calc_max_growth_rate)

    @property
    def has_profit(self):
        return self._data_cache.get('has_profit', lambda: self.profit_with_fee > 0)

    @property
    def max_profit_rate(self):
        return self._data_cache.get('max_profit_rate',
                                    lambda: (self.break_even_price - self.avg_price) / self.avg_price)

    def pre_handle(self):
        self._indicators = self.init(self.data)

    def i(self, key):
        return self._indicators[key].loc[:self.today]

    def inter_handle(self):
        # 一定時間範圍內不做任何事以確保策略能正常運行（如讀取前一天的資料）
        if (self.market_data.current_time - self.market_data.start_time).days < self.preload_days:
            return

        self._day_action_cache = set()
        self._data_cache.clear()
        self._actions = []
        self.handle()


class SignalBase(abc.ABC):
    name = 'signal_base'
    params = {}

    def init(self, data):
        return {}

    @abc.abstractmethod
    def handle(self, strategy: StrategyBase):
        pass


class AndSignal(SignalBase):

    def __init__(self, *signals, reason=''):
        self.signals = signals
        self.reason = reason

        self._params = {}
        for signal in self.signals:
            self._params.update(signal.params)
        for signal in self.signals:
            signal.params = self._params

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params):
        self._params = params
        for signal in self.signals:
            signal.params = self._params

    def init(self, data):
        result = {}
        for signal in self.signals:
            result.update(signal.init(data))
        return result

    def handle(self, strategy: StrategyBase):
        reasons = []
        conditions = []
        for signal in self.signals:
            cond, reason = signal.handle(strategy)
            conditions.append(cond)
            reasons.append(reason)

        df = pd.concat(conditions, axis=1)
        df = df.fillna(False)
        cond = df.all(axis=1)
        return (
            cond,
            self.reason if self.reason else '&'.join(reasons)
        )


class SortSignalBase(SignalBase, abc.ABC):
    pass


class SignalStrategyBase(StrategyBase):
    buy_signals = []
    sell_signals = []
    sort_signal: SortSignalBase

    def __init__(self):
        self._params = {}
        for signal in [*self.buy_signals, *self.sell_signals, self.sort_signal]:
            self._params.update(signal.params)

        for signal in [*self.buy_signals, *self.sell_signals, self.sort_signal]:
            signal.params = self._params

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params):
        self._params = params
        for signal in [*self.buy_signals, *self.sell_signals, self.sort_signal]:
            signal.params = self._params

    def init(self, data):
        result = {}
        for signal in [*self.buy_signals, *self.sell_signals, self.sort_signal]:
            result = {
                **result,
                **signal.init(data),
            }
        return result

    # noinspection PyTypeChecker
    def handle(self):
        weight_s = self.sort_signal.handle(self)
        # 過濾權重為 0 的元素
        weight_s = weight_s[weight_s != 0]
        # 根據權重排序
        weight_s = weight_s.sort_values(ascending=False, kind='mergesort')

        for buy_signal in self.buy_signals:
            buy_cond, reason = buy_signal.handle(self)
            target_list = self.new_target_list([
                buy_cond
            ])

            # 提取排序後的索引並只保留在 l 中的元素
            target_list = [index for index in weight_s.index if index in target_list]

            for stock_id in target_list:
                if isinstance(reason, FunctionType):
                    reason = reason(stock_id)
                self.buy_next_day_market(stock_id, reason)

        for sell_signal in self.sell_signals:
            sell_cond, reason = sell_signal.handle(self)
            target_list = self.new_target_list([sell_cond])

            for stock_id in target_list:
                if isinstance(reason, FunctionType):
                    reason = reason(stock_id)
                self.sell_next_day_market(stock_id, note=reason)
