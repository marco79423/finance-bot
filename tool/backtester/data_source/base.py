import abc

import pandas as pd


class Product:

    def __init__(self, data_source: 'DataSourceBase', product_id):
        self._data_source = data_source
        self._product_id = product_id

    @property
    def open(self):
        return self._data_source.open[self._product_id]

    @property
    def close(self):
        return self._data_source.close[self._product_id]

    @property
    def high(self):
        return self._data_source.high[self._product_id]

    @property
    def low(self):
        return self._data_source.low[self._product_id]

    @property
    def volume(self):
        return self._data_source.volume[self._product_id]


class DataSourceBase(abc.ABC):
    is_limit = False

    def __init__(self, start=None, end=None):
        self._start_time = pd.Timestamp(start) if start else None
        self._current_time = self._start_time
        self._end_time = pd.Timestamp(end) if end else None

    def __getitem__(self, product_id) -> Product:
        return Product(self, product_id)

    def set_time(self, time):
        if self._start_time is None:
            self._start_time = time
        if self._end_time is None:
            self._end_time = time
        self._current_time = time

    @property
    def start_time(self):
        return self._start_time

    @property
    def current_time(self):
        return self._current_time

    @property
    def end_time(self):
        return self._end_time

    @property
    def open(self):
        end = self.current_time if self.is_limit else self.end_time
        return self.all_open[self.start_time:end]

    @property
    def close(self):
        end = self.current_time if self.is_limit else self.end_time
        return self.all_close[self.start_time:end]

    @property
    def high(self):
        end = self.current_time if self.is_limit else self.end_time
        return self.all_high[self.start_time:end]

    @property
    def low(self):
        end = self.current_time if self.is_limit else self.end_time
        return self.all_low[self.start_time:end]

    @property
    def volume(self):
        end = self.current_time if self.is_limit else self.end_time
        return self.all_volume[self.start_time:end]

    @property
    @abc.abstractmethod
    def all_open(self):
        pass

    @property
    @abc.abstractmethod
    def all_close(self):
        pass

    @property
    @abc.abstractmethod
    def all_high(self):
        pass

    @property
    @abc.abstractmethod
    def all_low(self):
        pass

    @property
    @abc.abstractmethod
    def all_volume(self):
        pass
