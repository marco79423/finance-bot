from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from finance_bot.model import Wallet, WalletLog


class WalletRepository:

    @staticmethod
    async def get_balance(session, code):
        wallet = await session.get(Wallet, code)
        return wallet.balance

    @staticmethod
    async def set_balance(session: AsyncSession, code, balance, description=''):
        async with session.begin():
            wallet = await session.get(Wallet, code)
            session.add(WalletLog(
                code=wallet.code,
                before=wallet.balance,
                amount=balance - wallet.balance,
                after=balance,
                description=description,
            ))

            wallet.balance = balance

    @staticmethod
    def sync_set_balance(session: Session, code, balance, description=''):
        with session.begin():
            wallet = session.get(Wallet, code)
            session.add(WalletLog(
                code=wallet.code,
                before=wallet.balance,
                amount=balance - wallet.balance,
                after=balance,
                description=description,
            ))

            wallet.balance = balance
