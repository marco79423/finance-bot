from sqlalchemy import Column, String, DateTime, func, Numeric, Index, BigInteger

from .base import Base


class WalletLog(Base):
    __tablename__ = 'wallet_log'
    __table_args__ = (
        Index('idx_code', 'code'),
    )

    id = Column(BigInteger, primary_key=True, comment='ID')
    code = Column(String(32), nullable=False, comment='錢包代號')
    before = Column(Numeric(precision=38, scale=18), nullable=False, comment='變化前的餘額')
    amount = Column(Numeric(precision=38, scale=18), nullable=False, comment='交易金額')
    after = Column(Numeric(precision=38, scale=18), nullable=False, comment='變化後的餘額')
    description = Column(String(100), comment='描述')

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
