import abc
import datetime as dt

from finance_bot.tw_stock.ticker_db.ticker_db import TickerDB, Ticker


class StrategyBase(abc.ABC):
    name: str

    def __init__(self, ticker_db: TickerDB):
        self.ticker_db = ticker_db

    @abc.abstractmethod
    def select_tickers(self, date: dt.datetime) -> [Ticker]:
        """挑選符合條件的股票"""
        pass

    def is_buy_point(self, symbol: str, date: dt.datetime) -> bool:
        """選擇適合的買點"""
        pass

    def is_sell_point(self, symbol: str, date: dt.datetime) -> bool:
        """選擇適合的賣點"""
        pass
