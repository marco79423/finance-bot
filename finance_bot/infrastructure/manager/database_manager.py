import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import create_async_engine

from finance_bot.infrastructure.manager.base import ManagerBase
from finance_bot.model.base import Base


class DatabaseManager(ManagerBase):
    COMMIT_GROUP_SIZE = 1000

    def __init__(self, infra):
        super().__init__(infra)
        self._engine = create_engine(
            self.conf.tw_stock.database.url,
            echo_pool=True,
            pool_pre_ping=True,
            pool_recycle=3600,  # 多少時間自動重連 (MySQL 預設會 8 小時踢人)
        )
        self._async_engine = create_async_engine(
            self.conf.tw_stock.database.async_url,
            echo_pool=True,
            pool_pre_ping=True,
            pool_recycle=3600,  # 多少時間自動重連 (MySQL 預設會 8 小時踢人)
        )
        self._migrated = False

    @property
    def engine(self):
        return self._engine

    @property
    def async_engine(self):
        return self._async_engine

    async def migrate(self):
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self._migrated = True

    async def batch_insert_or_update(self, session, model, df):
        if not self._migrated:
            await self.migrate()

        for _, group in df.groupby(df.index // self.COMMIT_GROUP_SIZE):
            for _, v in group.iterrows():
                await self.insert_or_update(session, model, v, False)
            await session.commit()

    async def insert_or_update(self, session, model, data, auto_commit=True):
        if not self._migrated:
            await self.migrate()

        # 移除 data 的空值不更新
        modified = {
            key: value if pd.notnull(value) else None
            for key, value in data.items()
        }

        insert_stmt = insert(model).values(**modified).on_duplicate_key_update(**modified)
        await session.execute(insert_stmt)
        if auto_commit:
            await session.commit()
