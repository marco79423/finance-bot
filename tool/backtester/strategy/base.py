import abc
from typing import Optional, List

from tool.backtester.broker import Broker


class StrategyBase(abc.ABC):
    name: str
    params: dict = {}

    stock_id: str
    broker: Broker
    available_stock_ids: Optional[List[str]] = None

    _buy_next_day_market = False
    _buy_next_day_market_note = ''
    _sell_next_day_market = False
    _sell_next_day_market_note = ''

    @abc.abstractmethod
    def handle(self):
        pass

    def buy_next_day_market(self, confident_score=1, note=''):
        """
        在隔天市價買入 (但在回測試會以買在最高價計算)
        :param confident_score:
        :return:
        """
        self._buy_next_day_market = True
        self._buy_next_day_market_note = note

    def sell_next_day_market(self, note=''):
        """
        在隔天市價賣出 (但在回測時會以賣在最低價計算)
        :return:
        """
        self._sell_next_day_market = True
        self._sell_next_day_market_note = note

    @property
    def data(self):
        return self.broker.stock_data(self.stock_id)

    @property
    def close(self):
        return self.data.close.iloc[-1]

    @property
    def volume(self):
        return self.data.volume.iloc[-1]

    @property
    def today(self):
        return self.broker.current_date

    @property
    def current_shares(self):
        trades = self.broker.open_trades.set_index('stock_id')
        return trades['shares'].get(self.stock_id, 0)

    @property
    def entry_date(self):
        trades = self.broker.open_trades.set_index('stock_id')
        return trades['start_date'].get(self.stock_id, None)

    @property
    def entry_price(self):
        trades = self.broker.open_trades.set_index('stock_id')
        return trades['start_price'].get(self.stock_id, None)

    @property
    def break_even_price(self):
        fee_ratio = 1.425 / 1000 * self.broker.fee_discount  # 0.1425％
        tax_ratio = 3 / 1000  # 政府固定收 0.3 %
        new_stock_price = self.entry_price * (1 + fee_ratio) / (1 - fee_ratio - tax_ratio)
        return new_stock_price

    @property
    def has_profit(self):
        return self.close > self.break_even_price

    def inter_handle(self):
        self._buy_next_day_market = False
        self._sell_next_day_market = False

        try:
            self.handle()
        except Exception as e:
            """失敗就當作沒這回事"""
            pass
