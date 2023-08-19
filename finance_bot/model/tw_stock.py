from sqlalchemy import Column, String, DateTime, func, Boolean, Index

from .base import Base


class TWStock(Base):
    __tablename__ = 'tw_stock'
    __table_args__ = (
        Index('idx_instrument_type', 'instrument_type'),
        Index('idx_tracked', 'tracked'),
    )

    stock_id = Column(String(32), primary_key=True, comment='股票 ID')
    name = Column(String(60), default='', comment='證券名稱')
    instrument_type = Column(String(32), default='', comment='金融商品類型')
    industry = Column(String(60), default='', comment='產業別')
    listing_date = Column(DateTime, comment='上市日')
    tracked = Column(Boolean, nullable=False, default=True, comment='是否追蹤此股票的資訊')

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
