import pandas as pd
from sqlalchemy import text

from .stock_getter import StockGetter
from ...infrastructure import infra


class DataGetter:

    def __init__(self):
        self._prices_df = None
        self._monthly_revenue_df = None
        self._financial_statements_df = None

    def __getitem__(self, stock_id):
        return StockGetter(stock_id)

    @property
    def open(self):
        df = self._get_prices_df()
        return df.pivot(columns='stock_id', values='open')

    @property
    def close(self):
        df = self._get_prices_df()
        return df.pivot(columns='stock_id', values='close')

    @property
    def high(self):
        df = self._get_prices_df()
        return df.pivot(columns='stock_id', values='high')

    @property
    def low(self):
        df = self._get_prices_df()
        return df.pivot(columns='stock_id', values='low')

    @property
    def volume(self):
        df = self._get_prices_df()
        return df.pivot(columns='stock_id', values='volume')

    @property
    def traded_value(self):
        df = self._get_prices_df()
        return df.pivot(columns='stock_id', values='traded_value')

    @property
    def transaction_count(self):
        df = self._get_prices_df()
        return df.pivot(columns='stock_id', values='transaction_count')

    @property
    def monthly_revenue(self):
        if self._monthly_revenue_df is None:
            df = pd.read_sql(
                sql=text("SELECT date, stock_id, revenue FROM tw_stock_monthly_revenue"),
                con=infra.db.engine,
            )
            df['date'] = pd.to_datetime(df['date']).dt.to_period('M')
            df = df.set_index('date')
            self._monthly_revenue_df = df.pivot(columns='stock_id', values='revenue')
        return self._monthly_revenue_df

    @property
    def share_capital(self):
        df = self._get_financial_statements_df()
        return df.pivot(columns='stock_id', values='share_capital')

    def _get_prices_df(self):
        if self._prices_df is None:
            self._prices_df = pd.read_sql(
                sql=text("SELECT * FROM tw_stock_price"),
                con=infra.db.engine,
                index_col='date',
                parse_dates=['date'],
            )
        return self._prices_df

    def _get_financial_statements_df(self):
        if self._financial_statements_df is None:
            df = pd.read_sql(
                sql=text("SELECT * FROM tw_stock_financial_statements"),
                con=infra.db.engine,
                index_col='date',
            )
            df.index = df.index.astype('period[Q]')
            self._financial_statements_df = df
        return self._financial_statements_df
