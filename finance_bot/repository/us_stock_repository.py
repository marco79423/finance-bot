from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert

from finance_bot.model import USStock


class USStockRepository:
    COMMIT_GROUP_SIZE = 1000

    async def set_stocks(self, session, stock_df):
        for _, group in stock_df.groupby(stock_df.index // self.COMMIT_GROUP_SIZE):
            for _, v in group.iterrows():
                insert_stmt = insert(USStock).values(**v).on_duplicate_key_update(**v)
                await session.execute(insert_stmt)

    @staticmethod
    async def get_stocks(session):
        result = await session.scalars(
            select(USStock)
        )
        return list(result)

    def sync_set_stocks(self, session, stock_df):
        for _, group in stock_df.groupby(stock_df.index // self.COMMIT_GROUP_SIZE):
            for _, v in group.iterrows():
                insert_stmt = insert(USStock).values(**v).on_duplicate_key_update(**v)
                session.execute(insert_stmt)
