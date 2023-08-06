import pandas as pd
from sqlalchemy import text

from finance_bot.infrastructure import infra


class StockGetter:

    def __init__(self, stock_id):
        self.stock_id = stock_id
        self._prices_df = None
        self._monthly_revenue_s = None

    @property
    def open(self):
        df = self._get_prices_df()
        return df['open']

    @property
    def close(self):
        df = self._get_prices_df()
        return df['close']

    @property
    def monthly_revenue(self):
        if self._monthly_revenue_s is None:
            df = pd.read_sql(
                sql=text("SELECT date, revenue FROM tw_stock_monthly_revenue WHERE stock_id=:stock_id"),
                params={
                    'stock_id': str(self.stock_id),  # 確保輸入的是字串
                },
                con=infra.db.engine,
            )
            df['date'] = pd.to_datetime(df['date']).dt.to_period('M')
            df.set_index('date')
            self._monthly_revenue_s = df['revenue']
        return self._monthly_revenue_s

    def _get_prices_df(self):
        if self._prices_df is None:
            self._prices_df = pd.read_sql(
                sql=text("SELECT * FROM tw_stock_price WHERE stock_id=:stock_id"),
                params={
                    'stock_id': str(self.stock_id),  # 確保輸入的是字串
                },
                con=infra.db.engine,
                index_col='date',
                parse_dates=['date'],
            )
        return self._prices_df
