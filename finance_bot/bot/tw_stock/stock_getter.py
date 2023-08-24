import pandas as pd
from sqlalchemy import text

from finance_bot.infrastructure import infra


class StockGetter:

    def __init__(self, stock_id):
        self.stock_id = stock_id
        self._prices_df = None
        self._monthly_revenue_s = None
        self._financial_statements_df = None

    @property
    def open(self):
        """取得開盤價"""
        df = self._get_prices_df()
        return df['open']

    @property
    def close(self):
        """取得收盤價"""
        df = self._get_prices_df()
        return df['close']

    @property
    def high(self):
        """取得最高價"""
        df = self._get_prices_df()
        return df['high']

    @property
    def low(self):
        """取得最低價"""
        df = self._get_prices_df()
        return df['low']

    @property
    def volume(self):
        """取得成交股數"""
        df = self._get_prices_df()
        return df['volume']

    @property
    def traded_value(self):
        """取得成交金額"""
        df = self._get_prices_df()
        return df['traded_value']

    @property
    def transaction_count(self):
        """取得成交筆數"""
        df = self._get_prices_df()
        return df['transaction_count']

    @property
    def last_bid_price(self):
        """取得最後揭示買價"""
        df = self._get_prices_df()
        return df['last_bid_price']

    @property
    def last_bid_volume(self):
        """取得最後揭示買量"""
        df = self._get_prices_df()
        return df['last_bid_volume']

    @property
    def last_ask_price(self):
        """取得最後揭示賣價"""
        df = self._get_prices_df()
        return df['last_ask_price']

    @property
    def last_ask_volume(self):
        """取得最後揭示賣量"""
        df = self._get_prices_df()
        return df['last_ask_volume']

    @property
    def share_capital(self):
        """取得股本 (仟元)"""
        df = self._get_financial_statements_df()
        return df['share_capital']

    @property
    def market_capitalization(self):
        """取得市值"""
        share_capital = self.share_capital.copy()
        share_capital.index = share_capital.index.to_timestamp()

        df = pd.DataFrame({
            'close': self.close,
            'share_capital': share_capital,
        })
        df = df.fillna(method='ffill')  # 用前面的值補缺失值
        df = df.dropna()
        return df['close'] * (df['share_capital'] * 1000 / 10)

    @property
    def monthly_revenue(self):
        """取得月營收"""
        if self._monthly_revenue_s is None:
            df = pd.read_sql(
                sql=text("SELECT date, revenue FROM tw_stock_monthly_revenue WHERE stock_id=:stock_id"),
                params={
                    'stock_id': str(self.stock_id),  # 確保輸入的是字串
                },
                con=infra.db.engine,
            )
            df['date'] = pd.to_datetime(df['date']).dt.to_period('M')
            df = df.set_index('date')
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

    def _get_financial_statements_df(self):
        if self._financial_statements_df is None:
            df = pd.read_sql(
                sql=text("SELECT * FROM tw_stock_financial_statements WHERE stock_id=:stock_id"),
                params={
                    'stock_id': str(self.stock_id),  # 確保輸入的是字串
                },
                con=infra.db.engine,
                index_col='date',
            )
            df.index = df.index.astype('period[Q]')
            self._financial_statements_df = df
        return self._financial_statements_df
