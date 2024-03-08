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
        wallet = await session.get(Wallet, code)
        session.add(WalletLog(
            code=wallet.code,
            before=wallet.balance,
            amount=balance - wallet.balance,
            after=balance,
            description=description,
        ))

        wallet.balance = balance
        await session.commit()

    @staticmethod
    async def increase_balance(session: AsyncSession, code, amount, description=''):
        wallet = await session.get(Wallet, code)
        session.add(WalletLog(
            code=wallet.code,
            before=wallet.balance,
            amount=amount,
            after=wallet.balance + amount,
            description=description,
        ))
        wallet.balance = wallet.balance + amount
        await session.commit()

    @staticmethod
    async def decrease_balance(session: AsyncSession, code, amount, description=''):
        wallet = await session.get(Wallet, code)
        session.add(WalletLog(
            code=wallet.code,
            before=wallet.balance,
            amount=-amount,
            after=wallet.balance - amount,
            description=description,
        ))
        wallet.balance = wallet.balance - amount
        await session.commit()

    @staticmethod
    def sync_set_balance(session: Session, code, balance, description=''):
        wallet = session.get(Wallet, code)
        session.add(WalletLog(
            code=wallet.code,
            before=wallet.balance,
            amount=balance - wallet.balance,
            after=balance,
            description=description,
        ))

        wallet.balance = balance
        session.commit()
