import abc

import pandas as pd


class MarketDataBase(abc.ABC):
    @property
    @abc.abstractmethod
    def open(self) -> pd.DataFrame:
        pass

    @property
    @abc.abstractmethod
    def close(self) -> pd.DataFrame:
        pass

    @property
    @abc.abstractmethod
    def high(self) -> pd.DataFrame:
        pass

    @property
    @abc.abstractmethod
    def low(self) -> pd.DataFrame:
        pass


class StockDataBase:
    pass
