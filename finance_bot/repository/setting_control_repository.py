from sqlalchemy.ext.asyncio import AsyncSession

from finance_bot.model import SettingControl


class SettingControlRepository:

    @staticmethod
    async def is_enabled(session: AsyncSession, code):
        setting_control = await session.get(SettingControl, code)
        return setting_control.enabled

    @staticmethod
    async def enable(session: AsyncSession, code):
        async with session.begin():
            setting_control = await session.get(SettingControl, code)
            setting_control.enabled = True
