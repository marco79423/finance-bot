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
                self._save_or_update_price_close(data)
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
                self._save_or_update_share_capital(data)
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
                self._save_or_update_free_cash_flow(data)
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
                self._save_or_update_earning_per_share(data)
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
                self._save_or_update_return_on_equity(data)
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
                self._save_or_update_operating_income(data)
            self.session.commit()

    def _save_or_update_price_close(self, data):
        row = self.session.scalar(
            select(FinlabPriceClose)
            .where(FinlabPriceClose.symbol == data['symbol'])
            .where(FinlabPriceClose.date == data['date'])
            .limit(1)
        )

        if row:
            self.session.execute(
                update(FinlabPriceClose)
                .where(FinlabPriceClose.symbol == data['symbol'])
                .where(FinlabPriceClose.date == data['date'])
                .values(**data)
            )
        else:
            self.session.add(FinlabPriceClose(**data))

    def _save_or_update_share_capital(self, data):
        row = self.session.scalar(
            select(FinlabShareCapital)
            .where(FinlabShareCapital.symbol == data['symbol'])
            .where(FinlabShareCapital.date == data['date'])
            .limit(1)
        )

        if row:
            self.session.execute(
                update(FinlabShareCapital)
                .where(FinlabShareCapital.symbol == data['symbol'])
                .where(FinlabShareCapital.date == data['date'])
                .values(**data)
            )
        else:
            self.session.add(FinlabShareCapital(**data))

    def _save_or_update_free_cash_flow(self, data):
        row = self.session.scalar(
            select(FinlabFreeCashFlow)
            .where(FinlabFreeCashFlow.symbol == data['symbol'])
            .where(FinlabFreeCashFlow.date == data['date'])
            .limit(1)
        )

        if row:
            self.session.execute(
                update(FinlabFreeCashFlow)
                .where(FinlabFreeCashFlow.symbol == data['symbol'])
                .where(FinlabFreeCashFlow.date == data['date'])
                .values(**data)
            )
        else:
            self.session.add(FinlabFreeCashFlow(**data))

    def _save_or_update_earning_per_share(self, data):
        row = self.session.scalar(
            select(FinlabEarningPerShare)
            .where(FinlabEarningPerShare.symbol == data['symbol'])
            .where(FinlabEarningPerShare.date == data['date'])
            .limit(1)
        )

        if row:
            self.session.execute(
                update(FinlabEarningPerShare)
                .where(FinlabEarningPerShare.symbol == data['symbol'])
                .where(FinlabEarningPerShare.date == data['date'])
                .values(**data)
            )
        else:
            self.session.add(FinlabEarningPerShare(**data))

    def _save_or_update_return_on_equity(self, data):
        row = self.session.scalar(
            select(FinlabReturnOnEquity)
            .where(FinlabReturnOnEquity.symbol == data['symbol'])
            .where(FinlabReturnOnEquity.date == data['date'])
            .limit(1)
        )

        if row:
            self.session.execute(
                update(FinlabReturnOnEquity)
                .where(FinlabReturnOnEquity.symbol == data['symbol'])
                .where(FinlabReturnOnEquity.date == data['date'])
                .values(**data)
            )
        else:
            self.session.add(FinlabReturnOnEquity(**data))

    def _save_or_update_operating_income(self, data):
        row = self.session.scalar(
            select(FinlabOperatingIncome)
            .where(FinlabOperatingIncome.symbol == data['symbol'])
            .where(FinlabOperatingIncome.date == data['date'])
            .limit(1)
        )

        if row:
            self.session.execute(
                update(FinlabOperatingIncome)
                .where(FinlabOperatingIncome.symbol == data['symbol'])
                .where(FinlabOperatingIncome.date == data['date'])
                .values(**data)
            )
        else:
            self.session.add(FinlabOperatingIncome(**data))


if __name__ == '__main__':
    from finance_bot.ticker_db.database import get_engine

    engine = get_engine()
    with Session(engine) as session:
        updater = FinlabUpdater(session)
        # updater.update_price_close()
        # updater.update_share_capital()
        # updater.update_free_cash_flow()
        # updater.update_earning_per_share()
        # updater.update_return_on_equity()
        updater.update_operating_income()
