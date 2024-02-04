from sqlalchemy import Column, String, DateTime, func, Numeric, Index

from .base import Base


class Wallet(Base):
    __tablename__ = 'wallet'
    __table_args__ = (
        Index('idx_currency_code', 'currency_code'),
    )

    code = Column(String(32), primary_key=True, comment='錢包代號')
    name = Column(String(60), nullable=False, comment='錢包名稱')
    currency_code = Column(String(10), nullable=False, comment='幣別代號')
    balance = Column(Numeric(precision=38, scale=18), nullable=False, default=0, comment='餘額')

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
