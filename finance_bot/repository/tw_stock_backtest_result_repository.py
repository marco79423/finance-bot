from sqlalchemy import select

from finance_bot.model.tw_stock_backtest_result import TWStockBacktestResult


class TWStockBacktestResultRepository:

    @staticmethod
    async def add_result(session, signature, strategy_name, params, init_balance, final_balance, start_time, end_time):
        async with session.begin():
            session.add(TWStockBacktestResult(
                signature=signature,
                strategy_name=strategy_name,
                params=params,
                init_balance=init_balance,
                final_balance=final_balance,
                start_time=start_time,
                end_time=end_time,
            ))

    @staticmethod
    async def get_result(session, signature):
        return await  session.scalar(
            select(TWStockBacktestResult)
            .where(TWStockBacktestResult.signature == signature)
            .limit(1)
        )

    @staticmethod
    def sync_add_result(session, signature, strategy_name, params, init_balance, final_balance, start_time,
                              end_time):
        with session.begin():
            session.add(TWStockBacktestResult(
                signature=signature,
                strategy_name=strategy_name,
                params=params,
                init_balance=init_balance,
                final_balance=final_balance,
                start_time=start_time,
                end_time=end_time,
            ))

    @staticmethod
    def sync_get_result(session, signature):
        return session.scalar(
            select(TWStockBacktestResult)
            .where(TWStockBacktestResult.signature == signature)
            .limit(1)
        )
