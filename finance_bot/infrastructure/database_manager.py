import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import insert

from finance_bot.infrastructure.base import ManagerBase
from finance_bot.model.base import Base


class DatabaseManager(ManagerBase):
    COMMIT_GROUP_SIZE = 1000

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

    def batch_insert_or_update(self, session, model, df):
        for _, group in df.groupby(df.index // self.COMMIT_GROUP_SIZE):
            group.apply(lambda x: self._insert_or_update(session, model, x), axis=1)
            session.commit()

    @staticmethod
    def _insert_or_update(session, model, data):
        # 移除 data 的空值不更新
        modified = {
            key: value if pd.notnull(value) else None
            for key, value in data.items()
        }

        insert_stmt = insert(model).values(**modified).on_duplicate_key_update(**modified)
        session.execute(insert_stmt)
