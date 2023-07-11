from sqlalchemy import Column, String, DateTime, func, Index, Integer, Numeric

from .base import Base


class FinlabReturnOnEquity(Base):
    __tablename__ = 'finlab_return_on_equity'
    __table_args__ = (
        Index('idx_finlab_return_on_equity_date', 'date'),
        Index('uk_finlab_return_on_equity_symbol_date', 'symbol', 'date', unique=True),
    )

    id = Column(Integer, primary_key=True)
    symbol = Column(String(32), nullable=False)
    value = Column(Numeric(precision=65, scale=8), nullable=False)
    date = Column(String(8), nullable=False)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
