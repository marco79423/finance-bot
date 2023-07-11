import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from finance_bot.ticker_db.database import get_engine
from finance_bot.ticker_db.updater import FinlabUpdater, FinmindUpdater


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
        if 'market_capitalization' not in self._cache.index:
            self._cache['market_capitalization'] = self._cache['close'] * self._cache['share_capital'] / 10
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
        if 'operating_income_growth_rate' not in self._cache.index:
            self._cache[
                'operating_income_growth_rate'] = self.get_operating_income() / self.get_operating_income().shift(4)
        return self._cache['operating_income_growth_rate'].copy()

    def get_all_metrics(self):
        if self._cache is None:
            self.load()
        return self._cache

    def empty(self):
        return self.get_close_prices().empty


class TickerDB:

    def __init__(self):
        self.engine = get_engine()
        self.session = Session(self.engine)

        self.finlab_updater = FinlabUpdater(self.session)
        self.finmind_updater = FinmindUpdater(self.session)

        self._ticker_cache = {}
        self._all_metrics_cache = None

    def get_ticker(self, symbol: str) -> Ticker:
        """取得指定 Ticker"""
        if not self._ticker_cache.get(symbol):
            self._ticker_cache[symbol] = Ticker(self, symbol)
        return self._ticker_cache[symbol]

    def get_all_tickers(self):
        """取得所有 Ticker"""
        df = pd.read_sql(
            sql=text("SELECT stock_id FROM finmind_taiwan_stock_info"),
            con=self.engine,
        )
        return [self.get_ticker(symbol=stock_id) for stock_id in df['stock_id']]

    def get_all_metrics(self, tickers: [Ticker] = None):
        if tickers is None:
            tickers = self.get_all_tickers()
        df = pd.concat(
            [ticker.get_all_metrics() for ticker in tickers if not ticker.empty()]
        )
        df = df.sort_index()
        return df


if __name__ == '__main__':
    ticker_db = TickerDB()
    # print(ticker_db.get_all_tickers())
    # print(ticker_db.get_all_tickers_with_all_metrics())
    ticker = ticker_db.get_ticker('1101')
    print(ticker.get_close_prices())
    print(ticker.get_share_capital())
    print(ticker.get_market_capitalization())
    print(ticker.get_free_cash_flow())
    print(ticker.get_earning_per_share())
    print(ticker.get_return_on_equity())
    print(ticker.get_operating_income_growth_rate(True))
