from sqlalchemy import Column, DateTime, func, Numeric, BigInteger

from .base import Base


class SettingCryptoLoan(Base):
    __tablename__ = 'setting_crypto_loan'

    id = Column(BigInteger, primary_key=True, comment='ID')
    reserve_amount = Column(Numeric(precision=38, scale=18), nullable=False, default=0, comment='保留金額')

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
