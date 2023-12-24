import abc


class StockData:

    def __init__(self, market_data: 'MarketDataBase', product_id):
        self._market_data = market_data
        self._product_id = product_id

    @property
    def open(self):
        return self._market_data.open[self._product_id]

    @property
    def close(self):
        return self._market_data.close[self._product_id]

    @property
    def high(self):
        return self._market_data.high[self._product_id]

    @property
    def low(self):
        return self._market_data.low[self._product_id]

    @property
    def volume(self):
        return self._market_data.volume[self._product_id]


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
