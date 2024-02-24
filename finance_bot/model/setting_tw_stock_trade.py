from sqlalchemy import Column, DateTime, func, Boolean, BigInteger, String

from .base import Base


class SettingTWStockTrade(Base):
    __tablename__ = 'setting_tw_stock_trade'

    node_id = Column(String(32), primary_key=True, nullable=False, default='', comment='Node ID')
    auto_trade_enabled = Column(Boolean, nullable=False, comment='自動交易')

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
