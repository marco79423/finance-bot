import abc


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
