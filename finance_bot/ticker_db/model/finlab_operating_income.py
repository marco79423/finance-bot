from sqlalchemy import Column, String, DateTime, func, Index, Integer, Numeric

from .base import Base


class FinlabOperatingIncome(Base):
    __tablename__ = 'finlab_operating_income'
    __table_args__ = (
        Index('idx_finlab_operating_income_date', 'date'),
        Index('uk_finlab_operating_income_symbol_date', 'symbol', 'date', unique=True),
    )

    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    value = Column(Numeric(precision=18, scale=8), nullable=False)
    date = Column(String, nullable=False)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
