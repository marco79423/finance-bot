from sqlalchemy import Column, DateTime, func, Boolean, BigInteger

from .base import Base


class SettingTWStockTrade(Base):
    __tablename__ = 'setting_tw_stock_trade'

    id = Column(BigInteger, primary_key=True, comment='ID')
    auto_trade_enabled = Column(Boolean, nullable=False, comment='自動交易')

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
