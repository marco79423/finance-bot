import finlab
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from finance_bot.config import conf
from finance_bot.ticker_db.model.finlab_price_close import FinlabPriceClose


def get_finlab_data_loader():
    finlab.login(api_token=conf.ticker_db.updater.finlab.api_token)
    return finlab.data


class FinlabUpdater:
    def __init__(self):
        self.data_loader = get_finlab_data_loader()

    def update_price_close(self, session):
        df = self.data_loader.get('price:收盤價')

        for date, price_data in df.iterrows():
            print(f'Download {date} ...')
            price_data.dropna(inplace=True)
            for symbol, price in price_data.items():
                data = {
                    'date': date.to_pydatetime(),   # Must be native datetime for SQLAlchemy with sqlite3
                    'symbol': symbol,
                    'price': price,
                }
                self._save_or_update_price_close(session, data)
            session.commit()

    @staticmethod
    def _save_or_update_price_close(session, data):
        ticker = session.scalar(
            select(FinlabPriceClose)
            .where(FinlabPriceClose.symbol == data['symbol'])
            .where(FinlabPriceClose.date == data['date'])
            .limit(1)
        )

        if ticker:
            session.execute(
                update(FinlabPriceClose)
                .where(FinlabPriceClose.symbol == data['symbol'])
                .where(FinlabPriceClose.date == data['date'])
                .values(**data)
            )
        else:
            session.add(FinlabPriceClose(**data))


if __name__ == '__main__':
    from finance_bot.ticker_db.database import get_engine

    updater = FinlabUpdater()

    engine = get_engine()
    with Session(engine) as s:
        updater.update_price_close(s)
