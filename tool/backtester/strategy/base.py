import abc
from typing import Optional, List

from tool.backtester.broker import Broker
from tool.backtester.data_source import StockDataSource


class StrategyBase(abc.ABC):
    name: str
    params: dict = {}

    stock_id: str
    broker: Broker
    data_source: StockDataSource
    available_stock_ids: Optional[List[str]] = None

    _buy_next_day_market = False
    _buy_next_day_market_note = ''
    _sell_next_day_market = False
    _sell_next_day_market_note = ''

    _current = {}
    _indicators = {}

    def init(self, all_data):
        return {}

    @abc.abstractmethod
    def handle(self):
        pass

    def buy_next_day_market(self, confident_score=1, note=''):
        """
        在隔天市價買入 (但在回測試會以買在最高價計算)
        :param note:
        :param confident_score:
        :return:
        """
        self._buy_next_day_market = True
        self._buy_next_day_market_note = note
        self._current = {}

    def sell_next_day_market(self, note=''):
        """
        在隔天市價賣出 (但在回測時會以賣在最低價計算)
        :return:
        """
        self._sell_next_day_market = True
        self._sell_next_day_market_note = note
        self._current = {}

    @property
    def data(self):
        return self.data_source.stock_data(self.stock_id)

    @property
    def close(self):
        return self.data.close.iloc[-1]

    @property
    def volume(self):
        return self.data.volume.iloc[-1]

    @property
    def today(self):
        return self.data_source.current_date

    @property
    def current_shares(self):
        if 'current_shares' not in self._current:
            trades = self.broker.open_trades.set_index('stock_id')
            self._current['current_shares'] = trades['shares'].get(self.stock_id, 0)
        return self._current['current_shares']

    @property
    def entry_date(self):
        if 'entry_date' not in self._current:
            trades = self.broker.open_trades.set_index('stock_id')
            self._current['entry_date'] = trades['start_date'].get(self.stock_id, None)
        return self._current['entry_date']

    @property
    def entry_price(self):
        if 'entry_price' not in self._current:
            trades = self.broker.open_trades.set_index('stock_id')
            self._current['entry_price'] = trades['start_price'].get(self.stock_id, None)
        return self._current['entry_price']

    @property
    def break_even_price(self):
        if 'break_even_price' not in self._current:
            fee_ratio = 1.425 / 1000 * self.broker.fee_discount  # 0.1425％
            tax_ratio = 3 / 1000  # 政府固定收 0.3 %
            self._current['break_even_price'] = self.entry_price * (1 + fee_ratio) / (1 - fee_ratio - tax_ratio)
        return self._current['break_even_price']

    @property
    def has_profit(self):
        return self.close > self.break_even_price

    def pre_handle(self):
        self._indicators = self.init(self.data.raw)

    def i(self, key):
        return self._indicators[key].loc[:self.today]

    def inter_handle(self):
        self._buy_next_day_market = False
        self._sell_next_day_market = False

        try:
            self.handle()
        except Exception as e:
            """失敗就當作沒這回事"""
            pass
