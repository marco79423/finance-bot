import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from finance_bot.ticker_db.database import get_engine
from finance_bot.ticker_db.updater import FinlabUpdater, FinmindUpdater


class Ticker:
    def __init__(self, ticker_db: 'TickerDB', symbol: str):
        self.ticker_db = ticker_db
        self.symbol = symbol

    def get_close_prices(self) -> pd.Series:
        """取得收盤價"""
        df = pd.read_sql(
            sql=text("SELECT price, date FROM finlab_price_close WHERE symbol=:symbol"),
            params={'symbol': self.symbol},
            con=self.ticker_db.engine,
            index_col='date',
            parse_dates=['date'],
        )
        return df['price']

    def get_share_capitals(self) -> pd.Series:
        """取得股本"""
        df = pd.read_sql(
            sql=text("SELECT value, date FROM finlab_share_capital WHERE symbol=:symbol"),
            params={'symbol': self.symbol},
            con=self.ticker_db.engine,
            index_col='date',
        )
        df.index = pd.PeriodIndex(df.index, freq='Q')
        return df['value']

    def get_free_cash_flow(self) -> pd.Series:
        """取得自由現金流"""
        df = pd.read_sql(
            sql=text("SELECT value, date FROM finlab_free_cash_flow WHERE symbol=:symbol"),
            params={'symbol': self.symbol},
            con=self.ticker_db.engine,
            index_col='date',
        )
        df.index = pd.PeriodIndex(df.index, freq='Q')
        return df['value']

    def get_earning_per_share(self) -> pd.Series:
        """取得每股稅後淨利(EPS)"""
        df = pd.read_sql(
            sql=text("SELECT value, date FROM finlab_earning_per_share WHERE symbol=:symbol"),
            params={'symbol': self.symbol},
            con=self.ticker_db.engine,
            index_col='date',
        )
        df.index = pd.PeriodIndex(df.index, freq='Q')
        return df['value']

    def get_return_on_equity(self) -> pd.Series:
        """取得股東權益報酬率(ROE)"""
        df = pd.read_sql(
            sql=text("SELECT value, date FROM finlab_return_on_equity WHERE symbol=:symbol"),
            params={'symbol': self.symbol},
            con=self.ticker_db.engine,
            index_col='date',
        )
        df.index = pd.PeriodIndex(df.index, freq='Q')
        return df['value']

    def get_operating_income(self) -> pd.Series:
        """取得營業利益"""
        df = pd.read_sql(
            sql=text("SELECT value, date FROM finlab_operating_income WHERE symbol=:symbol"),
            params={'symbol': self.symbol},
            con=self.ticker_db.engine,
            index_col='date',
        )
        df.index = pd.PeriodIndex(df.index, freq='Q')
        return df['value']

class TickerDB:

    def __init__(self):
        self.engine = get_engine()
        self.session = Session(self.engine)

        self.finlab_updater = FinlabUpdater(self.session)
        self.finmind_updater = FinmindUpdater(self.session)

        self._ticker_cache = {}

    def get_ticker(self, symbol: str) -> Ticker:
        if not self._ticker_cache.get(symbol):
            self._ticker_cache[symbol] = Ticker(self, symbol)
        return self._ticker_cache[symbol]


if __name__ == '__main__':
    ticker_db = TickerDB()
    ticker = ticker_db.get_ticker('1101')
    # print(ticker.get_close_prices())
    # print(ticker.get_share_capitals())
    # print(ticker.get_free_cash_flow())
    # print(ticker.get_earning_per_share())
    # print(ticker.get_return_on_equity())
    print(ticker.get_operating_income())
