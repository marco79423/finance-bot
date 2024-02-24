from sqlalchemy import Column, DateTime, func, Numeric, String

from .base import Base


class SettingCryptoLoan(Base):
    __tablename__ = 'setting_crypto_loan'

    node_id = Column(String(32), primary_key=True, nullable=False, default='', comment='Node ID')
    reserve_amount = Column(Numeric(precision=38, scale=18), nullable=False, default=0, comment='保留金額')

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
