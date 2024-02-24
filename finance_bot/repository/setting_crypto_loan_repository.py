from sqlalchemy.ext.asyncio import AsyncSession

from finance_bot.infrastructure import infra
from finance_bot.model import SettingCryptoLoan


class SettingCryptoLoanRepository:

    def __init__(self):
        self._note_id = infra.conf.app.node_id

    async def get_reserve_amount(self, session: AsyncSession):
        setting_crypto_loan = await session.get(SettingCryptoLoan, self._note_id)
        return setting_crypto_loan.reserve_amount

    @staticmethod
    async def set_amount(self, session: AsyncSession, amount):
        async with session.begin():
            setting_reserve_amount = await session.get(SettingCryptoLoan, self._note_id)
            setting_reserve_amount.amount = amount
