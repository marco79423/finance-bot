from sqlalchemy import insert, select

from finance_bot.model import TWStockBacktestTradeLog


class TWStockBacktestTradeLogRepository:

    @staticmethod
    async def add_logs(session, trade_logs):
        session.execute(
            insert(TWStockBacktestTradeLog),
            trade_logs,
        )
        await session.commit()

    @staticmethod
    async def get_logs(session, signature):
        result = await session.scalars(
            select(TWStockBacktestTradeLog).
            where(TWStockBacktestTradeLog.signature == signature).
            order_by(TWStockBacktestTradeLog.index)
        )
        return list(result)

    @staticmethod
    def sync_add_logs(session, trade_logs):
        session.execute(
            insert(TWStockBacktestTradeLog),
            trade_logs,
        )

    @staticmethod
    def sync_get_logs(session, signature):
        result = session.scalars(
            select(TWStockBacktestTradeLog).
            where(TWStockBacktestTradeLog.signature == signature).
            order_by(TWStockBacktestTradeLog.id)
        )
        return list(result)
