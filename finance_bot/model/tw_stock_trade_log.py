from sqlalchemy import Column, String, DateTime, func, Index, BigInteger, Integer, Numeric

from .base import Base


class TWStockTradeLog(Base):
    __tablename__ = 'tw_stock_trade_log'
    __table_args__ = (
        Index('idx_wallet_code_strategy_name_date', 'wallet_code', 'strategy_name', 'created_at'),
        Index('idx_date_wallet_code', 'wallet_code', 'created_at'),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='ID')
    wallet_code = Column(String(32), comment='錢包代號')
    strategy_name = Column(String(10), comment='策略名稱')
    action = Column(String(10))
    stock_id = Column(String(32), primary_key=True, nullable=False, comment='股票 ID')
    shares = Column(Integer, nullable=False, comment='股')
    price = Column(Numeric(precision=10, scale=4), nullable=False, comment='價格')
    fee = Column(Integer, nullable=False, comment='手續費')
    amount = Column(Integer, nullable=False, comment='金額')
    note = Column(String(32), nullable=False, comment='備註')

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
