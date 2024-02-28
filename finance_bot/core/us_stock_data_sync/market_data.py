from finance_bot.infrastructure import infra
from finance_bot.utility import Cache
from .base import MarketDataBase, StockData


def get_us_stock_df():
    return infra.db_cache.read(key='us_stock')


def get_stock_prices_df():
    return infra.db_cache.read(key='us_stock_price').sort_index()


class MarketData(MarketDataBase):

    def __init__(self):
        self._cache = Cache()

    def __getitem__(self, stock_id) -> StockData:
        return StockData(self, stock_id)

    def sync(self):
        self._cache.clear()

    @property
    def stocks(self):
        """股票"""
        return self._cache.get('stocks', self._get_us_stock_df)

    def _get_us_stock_df(self):
        return self._cache.get('get_us_stock_df', get_us_stock_df)

    @property
    def start_time(self):
        return self._cache.get('start_time', self._get_start_time)

    def _get_start_time(self):
        return self.prices.index.min()

    @property
    def current_time(self):
        return self.end_time

    @property
    def end_time(self):
        return self._cache.get('end_time', self._get_end_time)

    def _get_end_time(self):
        return self.prices.index.max()

    @property
    def all_stock_ids(self):
        """所有股票 ID (有價格的)"""
        return self.close.columns.tolist()

    @property
    def all_date_range(self):
        return self.close.loc[self.start_time:self.current_time].index  # 交易日

    def get_stock_high_price(self, stock_id):
        return self.high.loc[self.current_time, stock_id]

    def get_stock_low_price(self, stock_id):
        return self.low.loc[self.current_time, stock_id]

    def get_stock_open_price(self, stock_id):
        return self.open.loc[self.current_time, stock_id]

    def get_stock_close_price(self, stock_id):
        return self.close.loc[self.current_time, stock_id]

    @property
    def prices(self):
        return self._cache.get('prices', get_stock_prices_df)

    @property
    def open(self):
        return self._cache.get('open', self._get_open_df)

    def _get_open_df(self):
        return self.prices.pivot(columns='stock_id', values='open').ffill()  # 補完空值的開盤價

    @property
    def close(self):
        return self._cache.get('close', self._get_close_df)

    def _get_close_df(self):
        return self.prices.pivot(columns='stock_id', values='close').ffill()  # 補完空值的收盤價

    @property
    def high(self):
        return self._cache.get('high', self._get_high_df)

    def _get_high_df(self):
        return self.prices.pivot(columns='stock_id', values='high').ffill()  # 補完空值的最高價

    @property
    def low(self):
        return self._cache.get('low', self._get_low_df)

    def _get_low_df(self):
        return self.prices.pivot(columns='stock_id', values='low').ffill()  # 補完空值的最低價

    @property
    def volume(self):
        return self._cache.get('volume', self._get_volume_df)

    def _get_volume_df(self):
        return self.prices.pivot(columns='stock_id', values='volume').ffill()  # 補完空值的成交量
