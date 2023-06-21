from sqlalchemy import Column, String, DateTime, func, Index, Integer, Numeric

from .base import Base


class FinlabPriceClose(Base):
    __tablename__ = 'finlab_price_close'
    __table_args__ = (
        Index('idx_date', 'date'),
        Index('uk_stock_id_date', 'stock_id', 'date', unique=True),
    )

    id = Column(Integer, primary_key=True)
    stock_id = Column(String, nullable=False)
    price = Column(Numeric(precision=18, scale=8), nullable=False)
    date = Column(DateTime, nullable=False)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
