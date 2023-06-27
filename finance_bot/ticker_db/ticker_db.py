import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from finance_bot.ticker_db.database import get_engine
from finance_bot.ticker_db.updater import FinlabUpdater, FinmindUpdater


class Ticker:
    def __init__(self, ticker_db: 'TickerDB', symbol: str):
        self.ticker_db = ticker_db
        self.symbol = symbol
        self._metric_cache = {}

    def get_close_prices(self) -> pd.Series:
        """取得收盤價"""
        if self._metric_cache.get('close') is None:
            df = pd.read_sql(
                sql=text("SELECT price, date FROM finlab_price_close WHERE symbol=:symbol"),
                params={'symbol': self.symbol},
                con=self.ticker_db.engine,
                index_col='date',
                parse_dates=['date'],
            )
            self._metric_cache['close'] = df['price']
        return self._metric_cache['close']

    def get_share_capitals(self, to_date=False) -> pd.Series:
        """取得股本"""
        if self._metric_cache.get('share_capitals') is None:
            df = pd.read_sql(
                sql=text("SELECT value, date FROM finlab_share_capital WHERE symbol=:symbol"),
                params={'symbol': self.symbol},
                con=self.ticker_db.engine,
                index_col='date',
            )

            df.index = pd.PeriodIndex(df.index, freq='Q')
            if to_date:
                df.index = df.index.to_timestamp()

            self._metric_cache['share_capitals'] = df['value']
        return self._metric_cache['share_capitals']

    def get_market_capitalization(self) -> pd.Series:
        """取得市值"""
        if self._metric_cache.get('market_capitalization') is None:
            close = self.get_close_prices()
            share_capitals = self.get_share_capitals()
            df = pd.DataFrame({
                'close': close,
                'share_capitals': share_capitals,
            })
            df = df.fillna(method='ffill')
            self._metric_cache['market_capitalization'] = df['close'] * df['share_capitals'] / 10
        return self._metric_cache['market_capitalization']

    def get_free_cash_flow(self, to_date=False) -> pd.Series:
        """取得自由現金流"""
        if self._metric_cache.get('free_cash_flow') is None:
            df = pd.read_sql(
                sql=text("SELECT value, date FROM finlab_free_cash_flow WHERE symbol=:symbol"),
                params={'symbol': self.symbol},
                con=self.ticker_db.engine,
                index_col='date',
            )

            df.index = pd.PeriodIndex(df.index, freq='Q')
            if to_date:
                df.index = df.index.to_timestamp()

            self._metric_cache['free_cash_flow'] = df['value']
        return self._metric_cache['free_cash_flow']

    def get_earning_per_share(self, to_date=False) -> pd.Series:
        """取得每股稅後淨利(EPS)"""
        if self._metric_cache.get('earning_per_share') is None:
            df = pd.read_sql(
                sql=text("SELECT value, date FROM finlab_earning_per_share WHERE symbol=:symbol"),
                params={'symbol': self.symbol},
                con=self.ticker_db.engine,
                index_col='date',
            )

            df.index = pd.PeriodIndex(df.index, freq='Q')
            if to_date:
                df.index = df.index.to_timestamp()

            self._metric_cache['earning_per_share'] = df['value']
        return self._metric_cache['earning_per_share']

    def get_return_on_equity(self, to_date=False) -> pd.Series:
        """取得股東權益報酬率(ROE)"""
        if self._metric_cache.get('return_on_equity') is None:
            df = pd.read_sql(
                sql=text("SELECT value, date FROM finlab_return_on_equity WHERE symbol=:symbol"),
                params={'symbol': self.symbol},
                con=self.ticker_db.engine,
                index_col='date',
            )

            df.index = pd.PeriodIndex(df.index, freq='Q')
            if to_date:
                df.index = df.index.to_timestamp()

            self._metric_cache['return_on_equity'] = df['value']
        return self._metric_cache['return_on_equity']

    def get_operating_income(self, to_date=False) -> pd.Series:
        """取得營業利益"""
        if self._metric_cache.get('operating_income') is None:
            df = pd.read_sql(
                sql=text("SELECT value, date FROM finlab_operating_income WHERE symbol=:symbol"),
                params={'symbol': self.symbol},
                con=self.ticker_db.engine,
                index_col='date',
            )

            df.index = pd.PeriodIndex(df.index, freq='Q')
            if to_date:
                df.index = df.index.to_timestamp()

            self._metric_cache['operating_income'] = df['value']
        return self._metric_cache['operating_income']

    def get_all_metrics(self):
        df = pd.DataFrame({
            'symbol': self.symbol,
            'close': self.get_close_prices(),
            'share_capitals': self.get_share_capitals(to_date=True),
            'free_cash_flow': self.get_free_cash_flow(to_date=True),
            'earning_per_share': self.get_earning_per_share(to_date=True),
            'return_on_equity': self.get_return_on_equity(to_date=True),
            'operating_income': self.get_operating_income(to_date=True),
            'market_capitalization': self.get_market_capitalization(),
        })
        df = df.fillna(method='ffill')
        return df

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

    def get_all_tickers_with_all_metrics(self):
        if self._all_metrics_cache is None:
            tickers = self.get_all_tickers()
            self._all_metrics_cache = pd.concat(
                [ticker.get_all_metrics() for ticker in tickers if not ticker.empty()]
            )
        return self._all_metrics_cache


if __name__ == '__main__':
    ticker_db = TickerDB()
    # print(ticker_db.get_all_tickers())
    print(ticker_db.get_all_tickers_with_all_metrics())
    ticker = ticker_db.get_ticker('1101')
    # print(ticker.get_close_prices())
    # print(ticker.get_share_capitals())
    # print(ticker.get_free_cash_flow())
    # print(ticker.get_earning_per_share())
    # print(ticker.get_return_on_equity())
    # print(ticker.get_operating_income(to_date=True))
    print(ticker.get_all_metrics())
