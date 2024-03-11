from sqlalchemy.ext.asyncio import AsyncSession

from finance_bot.infrastructure import infra
from finance_bot.model import SettingTWStockTrade


class SettingTWStockTradeRepository:

    def __init__(self):
        self._note_id = infra.conf.app.node_id

    async def is_auto_trade_enabled(self, session: AsyncSession):
        setting_tw_stock_trade = await session.get(SettingTWStockTrade, self._note_id)
        return setting_tw_stock_trade.auto_trade_enabled

    async def enable(self, session: AsyncSession):
        setting_tw_stock_trade = await session.get(SettingTWStockTrade, self._note_id)
        setting_tw_stock_trade.auto_trade_enabled = True
