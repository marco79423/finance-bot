import pandas as pd
from sqlalchemy import update, text
from sqlalchemy.orm import Session

from finance_bot.core.tw_stock_legacy.ticker_db.model import Ticker
from finance_bot.core.tw_stock_legacy.ticker_db.updater import UpdaterBase


class TickerUpdater(UpdaterBase):
    def update(self):
        self.update_finlab_close_prices()
        self.update_finlab_share_capital()
        self.update_finlab_free_cash_flow()
        self.update_finlab_earning_per_share()
        self.update_finlab_return_on_equity()
        self.update_finlab_operating_income()
        self.update_finmind_taiwan_stock_info()

    def update_finlab_close_prices(self):
        """取得 Finlab 的收盤價"""
        df = pd.read_sql(
            sql=text("SELECT symbol, date, price AS close FROM finlab_price_close"),
            con=self.session.get_bind(),
            parse_dates=['date'],
        )

        for _, group in df.groupby(df.index // 1000):
            group.apply(lambda x: self.save_or_update(Ticker, x), axis=1)
            self.session.commit()

    def update_finlab_share_capital(self):
        """取得 Finlab 股本資訊"""
        base_df = pd.read_sql(
            sql=text("SELECT symbol, date FROM ticker"),
            con=self.session.get_bind(),
            parse_dates=['date'],
        )

        df = pd.read_sql(
            sql=text("SELECT symbol, date, value AS share_capital FROM finlab_share_capital"),
            con=self.session.get_bind(),
        )
        df['date'] = df['date'].apply(lambda x: pd.Period(x, freq='Q').to_timestamp())

        merged_df = base_df.merge(df, on=['symbol', 'date'], how='left')
        merged_df = merged_df.fillna(method='ffill')
        merged_df = merged_df.dropna()

        for _, group in merged_df.groupby(merged_df.index // 1000):
            group.apply(lambda data: self.save_or_update(Ticker, data), axis=1)
            self.session.commit()

    def update_finlab_free_cash_flow(self):
        """取得 Finlab 的自由現金流資訊"""
        print('更新 finlab_free_cash_flow ...')
        base_df = pd.read_sql(
            sql=text("SELECT symbol, date FROM ticker"),
            con=engine,
            parse_dates=['date'],
        )

        df = pd.read_sql(
            sql=text("SELECT symbol, date, value AS free_cash_flow FROM finlab_free_cash_flow"),
            con=engine,
        )
        df['date'] = df['date'].apply(lambda x: pd.Period(x, freq='Q').to_timestamp())

        merged_df = base_df.merge(df, on=['symbol', 'date'], how='left')
        merged_df = merged_df.fillna(method='ffill')
        merged_df = merged_df.dropna()

        for _, group in merged_df.groupby(merged_df.index // 1000):
            group.apply(lambda data: self.save_or_update(Ticker, data), axis=1)
            self.session.commit()
            print('commit 1000 rows ...')

    def update_finlab_earning_per_share(self):
        """取得 Finlab 的每股稅後淨利"""
        base_df = pd.read_sql(
            sql=text("SELECT symbol, date FROM ticker"),
            con=engine,
            parse_dates=['date'],
        )

        df = pd.read_sql(
            sql=text("SELECT symbol, date, value AS earning_per_share FROM finlab_earning_per_share"),
            con=engine,
        )
        df['date'] = df['date'].apply(lambda x: pd.Period(x, freq='Q').to_timestamp())

        merged_df = base_df.merge(df, on=['symbol', 'date'], how='left')
        merged_df = merged_df.fillna(method='ffill')
        merged_df = merged_df.dropna()

        for _, group in merged_df.groupby(merged_df.index // 1000):
            group.apply(lambda data: self.save_or_update(Ticker, data), axis=1)
            self.session.commit()

    def update_finlab_return_on_equity(self):
        """取得 Finlab 股東權益報酬率(ROE)"""
        base_df = pd.read_sql(
            sql=text("SELECT symbol, date FROM ticker"),
            con=engine,
            parse_dates=['date'],
        )

        df = pd.read_sql(
            sql=text("SELECT symbol, date, value AS return_on_equity FROM finlab_return_on_equity"),
            con=engine,
        )
        df['date'] = df['date'].apply(lambda x: pd.Period(x, freq='Q').to_timestamp())

        merged_df = base_df.merge(df, on=['symbol', 'date'], how='left')
        merged_df = merged_df.fillna(method='ffill')
        merged_df = merged_df.dropna()

        for _, group in merged_df.groupby(merged_df.index // 1000):
            group.apply(lambda data: self.save_or_update(Ticker, data), axis=1)
            self.session.commit()

    def update_finlab_operating_income(self):
        """取得 Finlab 營業利益"""
        base_df = pd.read_sql(
            sql=text("SELECT symbol, date FROM ticker"),
            con=engine,
            parse_dates=['date'],
        )

        df = pd.read_sql(
            sql=text("SELECT symbol, date, value AS operating_income FROM finlab_operating_income"),
            con=engine,
        )
        df['date'] = df['date'].apply(lambda x: pd.Period(x, freq='Q').to_timestamp())

        merged_df = base_df.merge(df, on=['symbol', 'date'], how='left')
        merged_df = merged_df.fillna(method='ffill')
        merged_df = merged_df.dropna()

        for _, group in merged_df.groupby(merged_df.index // 1000):
            group.apply(lambda data: self.save_or_update(Ticker, data), axis=1)
            self.session.commit()

    def update_finmind_taiwan_stock_info(self):
        """取得 Finmind 的台股資訊"""
        df = pd.read_sql(
            sql=text("SELECT stock_id as symbol, stock_name as name, type FROM finmind_taiwan_stock_info"),
            con=self.session.get_bind(),
        )

        for _, data in df.iterrows():
            symbol = data['symbol']
            print(f'update {symbol} ...')
            stmt = (
                update(Ticker).
                where(Ticker.symbol == symbol).
                values(data)
            )
            self.session.execute(stmt)
            self.session.commit()


if __name__ == '__main__':
    from finance_bot.core.tw_stock_legacy.ticker_db.database import get_engine

    engine = get_engine()
    with Session(engine) as session:
        updater = TickerUpdater(session)
        # updater.update_finlab_close_prices()
        # updater.update_finlab_share_capital()
        # updater.update_finlab_free_cash_flow()
        # updater.update_finlab_return_on_equity()
        # updater.update_finlab_operating_income()
        updater.update_finmind_taiwan_stock_info()
