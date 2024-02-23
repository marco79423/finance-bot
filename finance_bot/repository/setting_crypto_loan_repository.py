from sqlalchemy.ext.asyncio import AsyncSession

from finance_bot.model import SettingCryptoLoan


class SettingCryptoLoanRepository:

    @staticmethod
    async def get_reserve_amount(session: AsyncSession):
        setting_crypto_loan = await session.get(SettingCryptoLoan, 1)
        return setting_crypto_loan.reserve_amount

    @staticmethod
    async def set_amount(session: AsyncSession, amount):
        async with session.begin():
            setting_reserve_amount = await session.get(SettingCryptoLoan, 1)
            setting_reserve_amount.amount = amount
