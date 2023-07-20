from sqlalchemy import Column, String, DateTime, func, Index

from .base import Base


class FinmindTaiwanStockInfo(Base):
    __tablename__ = 'finmind_taiwan_stock_info'
    __table_args__ = (
        Index('idx_finmind_taiwan_stock_info_industry_category', 'industry_category'),
        Index('idx_finmind_taiwan_stock_info_type', 'type'),
    )

    stock_id = Column(String(32), nullable=False, primary_key=True)
    industry_category = Column(String(32), nullable=False, default='')
    stock_name = Column(String(60), nullable=False, default='')
    type = Column(String(32), nullable=False, default='')
    date = Column(String(10), nullable=False)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
