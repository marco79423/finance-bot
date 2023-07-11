import finlab
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from finance_bot.config import conf
from finance_bot.ticker_db.model import FinlabPriceClose, FinlabShareCapital, FinlabFreeCashFlow, FinlabEarningPerShare, \
    FinlabReturnOnEquity, FinlabOperatingIncome
from finance_bot.ticker_db.updater.base import UpdaterBase


def get_finlab_data_loader():
    finlab.login(api_token=conf.ticker_db.updater.finlab.api_token)
    return finlab.data


class FinlabUpdater(UpdaterBase):
    def __init__(self, session):
        super().__init__(session)
        self.data_loader = get_finlab_data_loader()

    def update_price_close(self):
        df = self.data_loader.get('price:收盤價')

        for date, price_data in df.iterrows():
            print(f'Download {date} ...')
            price_data.dropna(inplace=True)
            for symbol, price in price_data.items():
                data = {
                    'date': date.to_pydatetime(),  # Must be native datetime for SQLAlchemy with sqlite3
                    'symbol': symbol,
                    'price': price,
                }
                self.save_or_update(FinlabPriceClose, data)
            self.session.commit()

    def update_share_capital(self):
        df = self.data_loader.get('financial_statement:股本')

        for date, value_data in df.iterrows():
            print(f'Download {date} ...')
            value_data.dropna(inplace=True)
            for symbol, value in value_data.items():
                data = {
                    'date': date,  # e.g. 2013-Q3
                    'symbol': symbol,
                    'value': value * 1000,  # 原單位為：仟元
                }
                self.save_or_update(FinlabShareCapital, data)
            self.session.commit()

    def update_free_cash_flow(self):
        df = self.data_loader.get('fundamental_features:自由現金流量')

        for date, value_data in df.iterrows():
            print(f'Download {date} ...')
            value_data.dropna(inplace=True)
            for symbol, value in value_data.items():
                data = {
                    'date': date,  # e.g. 2013-Q3
                    'symbol': symbol,
                    'value': value * 1000,  # 原單位為：仟元
                }
                self.save_or_update(FinlabFreeCashFlow, data)
            self.session.commit()

    def update_earning_per_share(self):
        df = self.data_loader.get('fundamental_features:每股稅後淨利')

        for date, value_data in df.iterrows():
            print(f'Download {date} ...')
            value_data.dropna(inplace=True)
            for symbol, value in value_data.items():
                data = {
                    'date': date,  # e.g. 2013-Q3
                    'symbol': symbol,
                    'value': value,  # 原單位為：元
                }
                self.save_or_update(FinlabEarningPerShare, data)
            self.session.commit()

    def update_return_on_equity(self):
        df = self.data_loader.get('fundamental_features:ROE稅後')

        for date, value_data in df.iterrows():
            print(f'Download {date} ...')
            value_data.dropna(inplace=True)
            for symbol, value in value_data.items():
                data = {
                    'date': date,  # e.g. 2013-Q3
                    'symbol': symbol,
                    'value': value,
                }
                self.save_or_update(FinlabReturnOnEquity, data)
            self.session.commit()

    def update_operating_income(self):
        df = self.data_loader.get('fundamental_features:營業利益')

        for date, value_data in df.iterrows():
            print(f'Download {date} ...')
            value_data.dropna(inplace=True)
            for symbol, value in value_data.items():
                data = {
                    'date': date,  # e.g. 2013-Q3
                    'symbol': symbol,
                    'value': value * 1000,  # 原單位為：仟元
                }
                self.save_or_update(FinlabOperatingIncome, data)
            self.session.commit()


if __name__ == '__main__':
    from finance_bot.ticker_db.database import get_engine

    engine = get_engine()
    with Session(engine) as session:
        updater = FinlabUpdater(session)
        updater.update_price_close()
        # updater.update_share_capital()
        # updater.update_free_cash_flow()
        # updater.update_earning_per_share()
        # updater.update_return_on_equity()
        # updater.update_operating_income()
