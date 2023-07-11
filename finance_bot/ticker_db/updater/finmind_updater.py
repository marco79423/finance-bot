from FinMind.data import DataLoader
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from finance_bot.config import conf
from finance_bot.ticker_db.model import FinmindTaiwanStockInfo
from finance_bot.ticker_db.updater import UpdaterBase


def get_finmind_data_loader():
    api = DataLoader()
    api.login_by_token(api_token=conf.ticker_db.updater.finmind.api_token)
    return api


class FinmindUpdater(UpdaterBase):
    def __init__(self, session):
        super().__init__(session)
        self.data_loader = get_finmind_data_loader()

    def update_taiwan_stock_info(self):
        df = self.data_loader.taiwan_stock_info()

        for _, data in df.iterrows():
            self.save_or_update(FinmindTaiwanStockInfo, data)
        self.session.commit()


if __name__ == '__main__':
    from finance_bot.ticker_db.database import get_engine

    engine = get_engine()
    with Session(engine) as session:
        updater = FinmindUpdater(session)
        updater.update_taiwan_stock_info()
