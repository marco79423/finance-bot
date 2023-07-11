from sqlalchemy import Column, String, DateTime, func, Index, Integer, Numeric

from .base import Base


class Ticker(Base):
    __tablename__ = 'ticker'
    __table_args__ = (
        Index('idx_ticker_symbol', 'symbol'),
        Index('idx_ticker_date', 'date'),
        Index('uk_ticker_symbol_date', 'symbol', 'date', unique=True)
    )

    id = Column(Integer, primary_key=True)
    symbol = Column(String(32), nullable=False)
    type = Column(String(32), default='')
    name = Column(String(60), default='')
    date = Column(DateTime, nullable=False)
    open = Column(Numeric(precision=65, scale=8))
    close = Column(Numeric(precision=65, scale=8))
    high = Column(Numeric(precision=65, scale=8))
    low = Column(Numeric(precision=65, scale=8))
    volume = Column(Numeric(precision=65, scale=8))
    earning_per_share = Column(Numeric(precision=65, scale=8))
    free_cash_flow = Column(Numeric(precision=65, scale=8))
    operating_income = Column(Numeric(precision=65, scale=8))
    return_on_equity = Column(Numeric(precision=65, scale=8))
    share_capital = Column(Numeric(precision=65, scale=8))

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
