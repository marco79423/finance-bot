from sqlalchemy import Column, String, DateTime, func, Index, Integer

from .base import Base


class TWStockMonthlyRevenue(Base):
    __tablename__ = 'tw_stock_monthly_revenue'
    __table_args__ = (
        Index('idx_stock_id', 'stock_id'),
        Index('idx_date', 'date'),
        Index('idx_revenue', 'revenue'),
    )

    stock_id = Column(String(16), primary_key=True, nullable=False, comment='股票 ID')
    date = Column(String(8), primary_key=True, nullable=False, comment='時間')
    revenue = Column(Integer, nullable=False, comment='月營收 (仟元)')

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
