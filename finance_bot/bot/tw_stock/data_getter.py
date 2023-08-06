import pandas as pd
from sqlalchemy import text

from .stock_getter import StockGetter
from ...infrastructure import infra


class DataGetter:

    def __init__(self):
        self._prices_df = None
        self._monthly_revenue_df = None

    def __getitem__(self, stock_id):
        return StockGetter(stock_id)

    @property
    def close(self):
        df = self._get_prices_df()
        return df.pivot(columns='stock_id', values='close')

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

    def _get_prices_df(self):
        if self._prices_df is None:
            self._prices_df = pd.read_sql(
                sql=text("SELECT * FROM tw_stock_price"),
                con=infra.db.engine,
                index_col='date',
                parse_dates=['date'],
            )
        return self._prices_df
