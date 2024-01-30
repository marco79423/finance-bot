import abc

import pandas as pd


class StockData:

    def __init__(self, market_data: 'MarketDataBase', stock_id):
        self.stock_id = stock_id

        self._market_data = market_data

    @property
    def prices(self):
        return self._market_data.prices[self._market_data.prices['stock_id'] == self.stock_id]

    @property
    def open(self):
        """取得開盤價"""
        return self._market_data.open[self.stock_id]

    @property
    def close(self):
        """取得收盤價"""
        return self._market_data.close[self.stock_id]

    @property
    def high(self):
        """取得最高價"""
        return self._market_data.high[self.stock_id]

    @property
    def low(self):
        """取得最低價"""
        return self._market_data.low[self.stock_id]

    @property
    def volume(self):
        """取得成交股數"""
        return self._market_data.volume[self.stock_id]

    @property
    def traded_value(self):
        """取得成交金額"""
        return self._market_data.traded_value[self.stock_id]

    @property
    def transaction_count(self):
        """取得成交筆數"""
        return self._market_data.transaction_count[self.stock_id]

    @property
    def share_capital(self):
        """取得股本 (仟元)"""
        return self._market_data.share_capital[self.stock_id]

    @property
    def total_shares_outstanding(self):
        """取得公司發行並且目前在外流通的股票總數"""
        return pd.Series(self.share_capital * 1000 / 10, name='total_shares_outstanding')

    @property
    def market_capitalization(self):
        """取得市值"""
        return self._market_data.market_capitalization[self.stock_id]

    @property
    def monthly_revenue(self) -> pd.Series:
        """取得月營收"""
        return self._market_data.monthly_revenue[self.stock_id]


class MarketDataBase(abc.ABC):

    @abc.abstractmethod
    def sync(self):
        pass

    @property
    @abc.abstractmethod
    def start_time(self):
        pass

    @property
    @abc.abstractmethod
    def current_time(self):
        pass

    @property
    @abc.abstractmethod
    def all_stock_ids(self):
        pass

    @property
    @abc.abstractmethod
    def all_date_range(self):
        pass

    @abc.abstractmethod
    def get_stock_high_price(self, stock_id):
        pass

    @abc.abstractmethod
    def get_stock_low_price(self, stock_id):
        pass

    @abc.abstractmethod
    def get_stock_open_price(self, stock_id):
        pass

    @abc.abstractmethod
    def get_stock_close_price(self, stock_id):
        pass

    @property
    @abc.abstractmethod
    def prices(self):
        pass

    @property
    @abc.abstractmethod
    def open(self):
        pass

    @property
    @abc.abstractmethod
    def close(self):
        pass

    @property
    @abc.abstractmethod
    def high(self):
        pass

    @property
    @abc.abstractmethod
    def low(self):
        pass

    @property
    @abc.abstractmethod
    def volume(self):
        pass

    @property
    @abc.abstractmethod
    def traded_value(self):
        """取得成交金額"""
        pass

    @property
    @abc.abstractmethod
    def transaction_count(self):
        """取得成交筆數"""
        pass

    @property
    @abc.abstractmethod
    def share_capital(self):
        """取得股本 (仟元)"""
        pass

    @property
    @abc.abstractmethod
    def total_shares_outstanding(self):
        """取得公司發行並且目前在外流通的股票總數"""
        pass

    @property
    @abc.abstractmethod
    def market_capitalization(self):
        """取得市值"""
        pass

    @property
    @abc.abstractmethod
    def monthly_revenue(self) -> pd.Series:
        """取得月營收"""
        pass
