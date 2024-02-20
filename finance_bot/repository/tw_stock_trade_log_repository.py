from finance_bot.model import TWStockTradeLog


class TWStockTradeLogRepository:

    @staticmethod
    async def add_log(session, wallet_code, strategy_name, action, stock_id, price, shares, fee, before, funds,
                      after, note):
        async with session.begin():
            session.add(TWStockTradeLog(
                wallet_code=wallet_code,
                strategy_name=strategy_name,
                action=action,
                stock_id=stock_id,
                shares=shares,
                price=price,
                fee=fee,
                before=before,
                funds=funds,
                after=after,
                note=note,
            ))

    @staticmethod
    def sync_add_log(session, wallet_code, strategy_name, action, stock_id, price, shares, fee, before, funds, after,
                     note):
        with session.begin():
            session.add(TWStockTradeLog(
                wallet_code=wallet_code,
                strategy_name=strategy_name,
                action=action,
                stock_id=stock_id,
                shares=shares,
                price=price,
                fee=fee,
                before=before,
                funds=funds,
                after=after,
                note=note,
            ))
