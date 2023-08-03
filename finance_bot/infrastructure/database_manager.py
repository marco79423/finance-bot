from sqlalchemy import create_engine

from finance_bot.infrastructure.base import ManagerBase
from finance_bot.model.base import Base


class DatabaseManager(ManagerBase):

    def __init__(self, infra):
        super().__init__(infra)
        self._engine = create_engine(
            self.conf.tw_stock.database.url,
            pool_recycle=3600,  # 多少時間自動重連 (MySQL 預設會 8 小時踢人)
        )

    def start(self):
        self.migrate()

    @property
    def engine(self):
        return self._engine

    def migrate(self):
        Base.metadata.create_all(bind=self.engine)
