from sqlalchemy import Column, String, Index, DateTime, func

from .base import Base


class TWStockTag(Base):
    __tablename__ = 'tw_stock_tag'
    __table_args__ = (
        Index('idx_stock_id', 'stock_id'),
        Index('idx_name', 'name'),
    )

    stock_id = Column(String(32), primary_key=True, nullable=False, comment='股票 ID')
    name = Column(String(60), primary_key=True, nullable=False, comment='標籤名稱')
    reason = Column(String(60), default='', comment='理由')

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
