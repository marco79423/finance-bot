import pandas as pd
from sqlalchemy import text

from .stock_getter import StockGetter
from ...infrastructure import infra


class DataGetter:

    def __init__(self, logger):
        self.use_cache = True

        self._logger = logger
        self._prices_df = None
        self._monthly_revenue_df = None
        self._financial_statements_df = None

    def __getitem__(self, stock_id):
        return StockGetter(stock_id)

    @property
    def open(self):
        df = self._get_prices_df(self.use_cache)
        return df.pivot(columns='stock_id', values='open')

    @property
    def close(self) -> pd.DataFrame:
        df = self._get_prices_df(self.use_cache)
        return df.pivot(columns='stock_id', values='close')

    @property
    def high(self):
        df = self._get_prices_df(self.use_cache)
        return df.pivot(columns='stock_id', values='high')

    @property
    def low(self):
        df = self._get_prices_df(self.use_cache)
        return df.pivot(columns='stock_id', values='low')

    @property
    def volume(self):
        df = self._get_prices_df(self.use_cache)
        return df.pivot(columns='stock_id', values='volume')

    @property
    def traded_value(self):
        df = self._get_prices_df(self.use_cache)
        return df.pivot(columns='stock_id', values='traded_value')

    @property
    def transaction_count(self):
        df = self._get_prices_df(self.use_cache)
        return df.pivot(columns='stock_id', values='transaction_count')

    @property
    def monthly_revenue(self):
        df = self._get_monthly_revenue_df(self.use_cache)
        return df.pivot(columns='stock_id', values='revenue')

    @property
    def share_capital(self):
        """取得股本"""
        df = self._get_financial_statements_df(self.use_cache)
        return df.pivot(columns='stock_id', values='share_capital')

    @property
    def total_shares_outstanding(self):
        """取得公司發行並且目前在外流通的股票總數"""
        return self.share_capital * 1000 / 10

    @property
    def market_capitalization(self):
        """取得市值"""
        close = self.close.copy()

        total_shares_outstanding = self.total_shares_outstanding.copy()
        total_shares_outstanding.index = total_shares_outstanding.index.to_timestamp()
        total_shares_outstanding = total_shares_outstanding.reindex(close.index).fillna(method='ffill')

        market_capitalization = close * total_shares_outstanding
        market_capitalization = market_capitalization.dropna(how='all')
        market_capitalization = market_capitalization.dropna(axis=1, how='all')

        return market_capitalization

    def rebuild_cache(self):
        mappings = [
            ('tw_stock_price', self._get_prices_df),
            ('tw_stock_monthly_revenue', self._get_monthly_revenue_df),
            ('tw_stock_financial_statements', self._get_financial_statements_df),
        ]

        for key, get_func in mappings:
            self._logger.info(f'重建 {key} 快取 ...')
            df = get_func(use_cache=False)
            infra.db_cache.save(key=key, df=df)

    def _get_prices_df(self, use_cache=True):
        if use_cache:
            if self._prices_df is None:
                self._prices_df = infra.db_cache.read(key='tw_stock_price')
            return self._prices_df
        else:
            self._prices_df = pd.read_sql(
                sql=text("SELECT * FROM tw_stock_price"),
                con=infra.db.engine,
                index_col='date',
                parse_dates=['date'],
            )
            return self._prices_df

    def _get_monthly_revenue_df(self, use_cache=True):
        if use_cache:
            if self._monthly_revenue_df is None:
                self._monthly_revenue_df = infra.db_cache.read(key='tw_stock_monthly_revenue')
            return self._monthly_revenue_df
        else:
            df = pd.read_sql(
                sql=text("SELECT date, stock_id, revenue FROM tw_stock_monthly_revenue"),
                con=infra.db.engine,
            )
            df['date'] = pd.to_datetime(df['date']).dt.to_period('M')
            df = df.set_index('date')
            self._monthly_revenue_df = df
            return self._monthly_revenue_df

    def _get_financial_statements_df(self, use_cache=True):
        if use_cache:
            if self._financial_statements_df is None:
                self._financial_statements_df = infra.db_cache.read(key='tw_stock_financial_statements')
            return self._financial_statements_df
        else:
            df = pd.read_sql(
                sql=text("SELECT * FROM tw_stock_financial_statements"),
                con=infra.db.engine,
                index_col='date',
            )
            df.index = df.index.astype('period[Q]')
            self._financial_statements_df = df
            return self._financial_statements_df
