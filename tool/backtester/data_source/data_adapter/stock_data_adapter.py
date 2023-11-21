from typing import List

import pandas as pd

from finance_bot.infrastructure import infra


class StockDataAdapter:

    def __init__(self, all_stock_ids=None, start=None, end=None):
        self._all_stock_ids = all_stock_ids
        self._start_time = pd.Timestamp(start) if start else None
        self._end_time = pd.Timestamp(end) if end else None

        df = infra.db_cache.read(key='tw_stock_price')
        df = df.sort_index()
        self._prices_df = df.loc[self._start_time:self._end_time]

        if self._start_time is None:
            self._start_time = self._prices_df.index.min()
        if self._end_time is None:
            self._end_time = self._prices_df.index.max()

        if self._all_stock_ids is None:
            self._all_stock_ids = self._prices_df['stock_id'].unique().tolist()
        else:
            self._prices_df = self._prices_df[self._prices_df['stock_id'].isin(self._all_stock_ids)]

        self._open = self._prices_df.pivot(columns='stock_id', values='open').ffill()  # 補完空值的收盤價
        self._close = self._prices_df.pivot(columns='stock_id', values='close').ffill()  # 補完空值的收盤價
        self._high = self._prices_df.pivot(columns='stock_id', values='high').ffill()  # 補完空值的最高價
        self._low = self._prices_df.pivot(columns='stock_id', values='low').ffill()  # 補完空值的最低價
        self._volume = self._prices_df.pivot(columns='stock_id', values='low').ffill()  # 補完空值的最低價

    @property
    def all_stock_ids(self) -> List[str]:
        return self._all_stock_ids

    @property
    def all_date_range(self) -> pd.DatetimeIndex:
        return self._close.index  # 交易日

    @property
    def start_time(self) -> pd.Timestamp:
        return self._start_time

    @property
    def end_time(self) -> pd.Timestamp:
        return self._end_time

    @property
    def open(self) -> pd.DataFrame:
        return self._open

    @property
    def close(self) -> pd.DataFrame:
        return self._close

    @property
    def high(self) -> pd.DataFrame:
        return self._high

    @property
    def low(self) -> pd.DataFrame:
        return self._low

    @property
    def volume(self) -> pd.DataFrame:
        return self._volume
