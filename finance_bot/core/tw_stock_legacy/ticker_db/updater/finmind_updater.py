from FinMind.data import DataLoader
from sqlalchemy.orm import Session

from finance_bot.infrastructure import infra
from finance_bot.core.tw_stock_legacy.ticker_db.model import FinmindTaiwanStockInfo
from finance_bot.core.tw_stock_legacy.ticker_db.updater import UpdaterBase


def get_finmind_data_loader():
    api = DataLoader()
    api.login_by_token(api_token=infra.conf.core.data_sync.updater.finmind.api_token)
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
    from finance_bot.core.tw_stock_legacy.ticker_db.database import get_engine

    engine = get_engine()
    with Session(engine) as session:
        updater = FinmindUpdater(session)
        updater.update_taiwan_stock_info()
