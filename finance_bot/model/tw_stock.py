from sqlalchemy import Column, String, DateTime, func, Index

from .base import Base


class TWStock(Base):
    __tablename__ = 'tw_stock'

    stock_id = Column(String(32), primary_key=True, comment='股票 ID')
    name = Column(String(60), default='', comment='證券名稱')
    industry = Column(String(60), default='', comment='產業別')
    listing_date = Column(DateTime, comment='上市日')

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())