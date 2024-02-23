from sqlalchemy.ext.asyncio import AsyncSession

from finance_bot.model import SettingReserveAmount


class SettingReserveAmountRepository:

    @staticmethod
    async def get_reserve_amount(session: AsyncSession, code):
        setting_reserve_amount = await session.get(SettingReserveAmount, code)
        return setting_reserve_amount.amount

    @staticmethod
    async def set_amount(session: AsyncSession, code, amount):
        async with session.begin():
            setting_reserve_amount = await session.get(SettingReserveAmount, code)
            setting_reserve_amount.amount = amount
