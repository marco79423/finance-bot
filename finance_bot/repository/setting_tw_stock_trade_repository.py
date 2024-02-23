from sqlalchemy.ext.asyncio import AsyncSession

from finance_bot.model import SettingTWStockTrade


class SettingTWStockTradeRepository:

    @staticmethod
    async def is_auto_trade_enabled(session: AsyncSession):
        setting_tw_stock_trade = await session.get(SettingTWStockTrade, 1)
        return setting_tw_stock_trade.auto_trade_enabled

    @staticmethod
    async def enable(session: AsyncSession):
        async with session.begin():
            setting_tw_stock_trade = await session.get(SettingTWStockTrade, 1)
            setting_tw_stock_trade.auto_trade_enabled = True
