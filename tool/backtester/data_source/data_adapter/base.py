import abc

import pandas as pd


class DataAdapterBase:

    def __init__(self, all_stock_ids=None, start=None, end=None):
        self._all_stock_ids = all_stock_ids
        self._start = pd.Timestamp(start) if start else None
        self._end = pd.Timestamp(end) if end else None

    @property
    def all_stock_ids(self):
        return self._all_stock_ids

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    @abc.abstractmethod
    def all_date_range(self):
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
