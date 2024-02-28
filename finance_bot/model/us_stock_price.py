from sqlalchemy import Column, String, DateTime, func, Index, Numeric, Integer

from .base import Base


class USStockPrice(Base):
    __tablename__ = 'us_stock_price'
    __table_args__ = (
        Index('idx_stock_id', 'stock_id'),
        Index('idx_date', 'date'),
    )

    stock_id = Column(String(32), primary_key=True, nullable=False, comment='股票 ID')
    date = Column(DateTime, primary_key=True, nullable=False, comment='時間')
    open = Column(Numeric(precision=10, scale=4), comment='開盤價')
    close = Column(Numeric(precision=10, scale=4), comment='收盤價')
    high = Column(Numeric(precision=10, scale=4), comment='最高價')
    low = Column(Numeric(precision=10, scale=4), comment='最低價')
    volume = Column(Integer, comment='成交股數')

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
