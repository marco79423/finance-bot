import abc
from typing import List

import pandas as pd

from finance_bot.infrastructure import infra


def get_stock_prices_df():
    return infra.db_cache.read(key='tw_stock_price').sort_index()


class DataAdapter(abc.ABC):

    def __init__(self, all_stock_ids=None, start=None, end=None):
        start_time = pd.Timestamp(start) if start else None
        end_time = pd.Timestamp(end) if end else None

        stock_prices_df = get_stock_prices_df()
        if start_time or end_time:
            stock_prices_df = stock_prices_df.loc[start_time:end_time]

        self._start_time = start_time or stock_prices_df.index.min()
        self._end_time = end_time or stock_prices_df.index.max()
        self._all_stock_ids = all_stock_ids or stock_prices_df['stock_id'].unique().tolist()

        stock_prices_df = stock_prices_df[stock_prices_df['stock_id'].isin(self._all_stock_ids)]
        self._open = stock_prices_df.pivot(columns='stock_id', values='open').ffill()  # 補完空值的收盤價
        self._close = stock_prices_df.pivot(columns='stock_id', values='close').ffill()  # 補完空值的收盤價
        self._high = stock_prices_df.pivot(columns='stock_id', values='high').ffill()  # 補完空值的最高價
        self._low = stock_prices_df.pivot(columns='stock_id', values='low').ffill()  # 補完空值的最低價
        self._volume = stock_prices_df.pivot(columns='stock_id', values='low').ffill()  # 補完空值的最低價

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