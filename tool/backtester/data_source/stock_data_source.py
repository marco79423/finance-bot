import pandas as pd

from finance_bot.core import TWStockManager
from tool.backtester.model import LimitMarketData


class StockDataSource:
    _data = TWStockManager().data

    def __init__(self, start, end):
        start = pd.Timestamp(start)
        end = pd.Timestamp(end)

        self._start_date = start
        self._current_date = None
        self._end_date = end

        self._all_close_prices = self._data.close.ffill()  # 補完空值的收盤價
        self._all_high_prices = self._data.high.ffill()  # 補完空值的最高價
        self._all_low_prices = self._data.low.ffill()  # 補完空值的最低價

        self._stock_data_cache = {}

    @property
    def all_close_prices(self):
        return self._all_close_prices

    @property
    def all_stock_ids(self):
        return self._data.close.columns

    def raw_stock_data(self, stock_id):
        return self._data[stock_id]

    def stock_data(self, stock_id):
        if stock_id not in self._stock_data_cache:
            self._stock_data_cache[stock_id] = LimitMarketData(
                self._data[stock_id],
                start_date=self._start_date,
                end_date=self._current_date,
            )
        self._stock_data_cache[stock_id].end_date = self._current_date
        return self._stock_data_cache[stock_id]

    def begin_date(self, date):
        if self._start_date is None:
            self._start_date = date
        self._current_date = date

    @property
    def all_date_range(self):
        return self._data.close.loc[self._start_date:self._end_date].index  # 交易日

    @property
    def start_date(self):
        return self._start_date

    @property
    def current_date(self):
        return self._current_date

    @property
    def end_date(self):
        return self._end_date

    def get_stock_high_price(self, stock_id):
        return self._all_high_prices.loc[self._current_date, stock_id]

    def get_stock_low_price(self, stock_id):
        return self._all_low_prices.loc[self._current_date, stock_id]

    def get_stock_close_price(self, stock_id):
        return self._all_close_prices.loc[self._current_date, stock_id]
