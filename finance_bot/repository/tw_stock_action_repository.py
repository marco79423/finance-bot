from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from finance_bot.model import TWStockAction


class TWStockActionRepository:

    @staticmethod
    async def get_buy_actions(session: AsyncSession):
        result = await session.scalars(
            select(TWStockAction).
            where(TWStockAction.operation == 'buy').
            order_by(TWStockAction.id)
        )
        return list(result)

    @staticmethod
    async def get_sell_actions(session: AsyncSession):
        result = await session.scalars(
            select(TWStockAction).
            where(TWStockAction.operation == 'sell').
            order_by(TWStockAction.id)
        )
        return list(result)

    @staticmethod
    async def set_actions(session: AsyncSession, actions):
        await session.execute(
            delete(TWStockAction)
        )
        if actions:
            await session.execute(
                insert(TWStockAction),
                actions,
            )
        await session.commit()

    @staticmethod
    def sync_get_buy_actions(session):
        return list(session.scalars(
            select(TWStockAction).
            where(TWStockAction.operation == 'buy').
            order_by(TWStockAction.id)
        ))

    @staticmethod
    def sync_set_actions(session, actions):
        session.execute(
            delete(TWStockAction)
        )
        session.execute(
            insert(TWStockAction),
            actions,
        )
        session.commit()
