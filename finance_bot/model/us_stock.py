from sqlalchemy import Column, String, DateTime, func, Index

from .base import Base


class USStock(Base):
    __tablename__ = 'us_stock'

    stock_id = Column(String(32), primary_key=True, comment='股票 ID')
    name = Column(String(60), default='', comment='證券名稱')

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
