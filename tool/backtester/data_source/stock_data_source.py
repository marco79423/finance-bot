from finance_bot.infrastructure import infra
from tool.backtester.data_source.base import DataSourceBase


class StockDataSource(DataSourceBase):

    def __init__(self, all_stock_ids=None, start=None, end=None):
        super().__init__(start, end)
        self._all_stock_ids = all_stock_ids

        df = infra.db_cache.read(key='tw_stock_price')
        df = df.sort_index()
        self._prices_df = df.loc[self.start_time:self.end_time]

        if self._all_stock_ids is None:
            self._all_stock_ids = self._prices_df['stock_id'].unique().tolist()
        else:
            self._prices_df = self._prices_df[self._prices_df['stock_id'].isin(self._all_stock_ids)]

        self._all_open = self._prices_df.pivot(columns='stock_id', values='open').ffill()  # 補完空值的收盤價
        self._all_close = self._prices_df.pivot(columns='stock_id', values='close').ffill()  # 補完空值的收盤價
        self._all_high = self._prices_df.pivot(columns='stock_id', values='high').ffill()  # 補完空值的最高價
        self._all_low = self._prices_df.pivot(columns='stock_id', values='low').ffill()  # 補完空值的最低價
        self._all_volume = self._prices_df.pivot(columns='stock_id', values='low').ffill()  # 補完空值的最低價

    @property
    def all_stock_ids(self):
        return self._all_stock_ids

    @property
    def all_date_range(self):
        return self._all_close.loc[self.current_time:self.end_time].index  # 交易日

    def get_stock_high_price(self, stock_id):
        return self._all_high.loc[self.current_time, stock_id]

    def get_stock_low_price(self, stock_id):
        return self._all_low.loc[self.current_time, stock_id]

    def get_stock_close_price(self, stock_id):
        return self._all_close.loc[self.current_time, stock_id]

    @property
    def all_open(self):
        return self._all_open

    @property
    def all_close(self):
        return self._all_close

    @property
    def all_high(self):
        return self._all_high

    @property
    def all_low(self):
        return self._all_low

    @property
    def all_volume(self):
        return self._all_volume
