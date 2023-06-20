from FinMind.data import DataLoader
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from finance_bot.config import conf
from finance_bot.ticker_db.model import FinmindTaiwanStockInfo


def get_finmind_loader():
    api = DataLoader()
    api.login_by_token(api_token=conf.ticker_db.updater.finmind.api_token)
    return api


class FinmindUpdater:
    def __init__(self):
        self.api = get_finmind_loader()

    def update_taiwan_stock_info(self, session):
        df = self.api.taiwan_stock_info()

        with Session(engine) as session:
            for _, data in df.iterrows():
                self._save_or_update_taiwan_stock_info(session, data)
            session.commit()

    @staticmethod
    def _save_or_update_taiwan_stock_info(session, data):
        ticker = session.scalar(
            select(FinmindTaiwanStockInfo)
            .where(FinmindTaiwanStockInfo.stock_id == data['stock_id'])
            .limit(1)
        )

        if ticker:
            session.execute(
                update(FinmindTaiwanStockInfo)
                .where(FinmindTaiwanStockInfo.stock_id == data['stock_id'])
                .values(**data)
            )
        else:
            session.add(FinmindTaiwanStockInfo(**data))


if __name__ == '__main__':
    from finance_bot.ticker_db.database import get_engine

    updater = FinmindUpdater()

    engine = get_engine()
    with Session(engine) as s:
        updater.update_taiwan_stock_info(s)
