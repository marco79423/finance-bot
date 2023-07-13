import pandas as pd
from sqlalchemy import text, select
from sqlalchemy.orm import Session

from finance_bot.tw_stock.ticker_db import model
from finance_bot.tw_stock.ticker_db.database import get_engine
from finance_bot.tw_stock.ticker_db.updater import FinlabUpdater, FinmindUpdater


class Ticker:
    def __init__(self, ticker_db: 'TickerDB', symbol: str):
        self.ticker_db = ticker_db
        self.symbol = symbol
        self._cache = None

    def load(self):
        df = pd.read_sql(
            sql=text("SELECT * FROM ticker WHERE symbol=:symbol"),
            params={'symbol': self.symbol},
            con=self.ticker_db.engine,
            index_col='date',
            parse_dates=['date'],
        )

        df['market_capitalization'] = df['close'] * df['share_capital'] / 10
        df['operating_income_growth_rate'] = df['operating_income'] / df['operating_income'].shift(4)

        df = df.fillna(method='ffill')
        df = df.sort_index()
        self._cache = df

    def get_close_prices(self) -> pd.Series:
        """取得收盤價"""
        if self._cache is None:
            self.load()
        return self._cache['close'].copy()

    def get_share_capital(self) -> pd.Series:
        """取得股本"""
        if self._cache is None:
            self.load()
        return self._cache['share_capital'].copy()

    def get_market_capitalization(self) -> pd.Series:
        """取得市值"""
        if self._cache is None:
            self.load()
        return self._cache['market_capitalization'].copy()

    def get_free_cash_flow(self) -> pd.Series:
        """取得自由現金流"""
        if self._cache is None:
            self.load()
        return self._cache['free_cash_flow'].copy()

    def get_earning_per_share(self) -> pd.Series:
        """取得每股稅後淨利(EPS)"""
        if self._cache is None:
            self.load()
        return self._cache['earning_per_share'].copy()

    def get_return_on_equity(self) -> pd.Series:
        """取得股東權益報酬率(ROE)"""
        if self._cache is None:
            self.load()
        return self._cache['return_on_equity'].copy()

    def get_operating_income(self) -> pd.Series:
        """取得營業利益"""
        if self._cache is None:
            self.load()
        return self._cache['operating_income'].copy()

    def get_operating_income_growth_rate(self, to_date=False) -> pd.Series:
        """取得營業利益成長率"""
        if self._cache is None:
            self.load()
        return self._cache['operating_income_growth_rate'].copy()

    def get_all_metrics(self, date=None):
        if self._cache is None:
            self.load()
        if date is not None:
            return self._cache[self._cache.index == date]
        return self._cache.copy()

    def empty(self):
        return self.get_close_prices().empty

    def __repr__(self):
        return f'Ticker<{self.symbol}>'


class TickerDB:

    def __init__(self):
        self.engine = get_engine()
        self.session = Session(self.engine)

        self._finlab_updater = None
        self._finmind_updater = None

        self._ticker_cache = {}
        self._all_metrics_cache = None

    @property
    def finlab_updater(self):
        if self._finlab_updater is None:
            self._finlab_updater = FinlabUpdater(self.session)
        return self._finlab_updater

    @property
    def finmind_updater(self):
        if self._finmind_updater is None:
            self._finmind_updater = FinmindUpdater(self.session)
        return self._finmind_updater

    def get_ticker(self, symbol: str) -> Ticker:
        """取得指定 Ticker"""
        if not self._ticker_cache.get(symbol):
            self._ticker_cache[symbol] = Ticker(self, symbol)
        return self._ticker_cache[symbol]

    def get_tickers(self, ticker_type=None, date=None):
        """取得 Ticker"""
        stmt = select(model.Ticker.symbol)
        if ticker_type is not None:
            stmt = stmt.where(model.Ticker.type == ticker_type)
        if date is not None:
            stmt = stmt.where(model.Ticker.date == date)
        stmt = stmt.distinct()
        return [self.get_ticker(symbol=symbol) for symbol, in self.session.execute(stmt).all()]

    def get_ticker_metrics(self, tickers: [Ticker] = None, date=None):
        if tickers is None:
            tickers = self.get_tickers(date=date)
        if not tickers:
            raise ValueError('tickers 輸入不合法')

        df = pd.concat(
            [ticker.get_all_metrics(date=date) for ticker in tickers if not ticker.empty()]
        )
        df = df.sort_index()
        return df


if __name__ == '__main__':
    ticker_db = TickerDB()
    print(len(ticker_db.get_tickers()))
    print(len(ticker_db.get_tickers(ticker_type='twse')))
    print(len(ticker_db.get_tickers(ticker_type='twse', date='2020-12-31')))
    # print(ticker_db.get_all_tickers_with_all_metrics())
    # ticker = ticker_db.get_ticker('1101')
    # print(ticker.get_close_prices())
    # print(ticker.get_share_capital())
    # print(ticker.get_market_capitalization())
    # print(ticker.get_free_cash_flow())
    # print(ticker.get_earning_per_share())
    # print(ticker.get_return_on_equity())
    # print(ticker.get_operating_income_growth_rate(True))
