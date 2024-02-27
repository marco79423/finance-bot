from sqlalchemy import Column, String, DateTime, func, Index, BigInteger, Integer, Numeric

from .base import Base


class TWStockBacktestTradeLog(Base):
    __tablename__ = 'tw_stock_backtest_trade_log'
    __table_args__ = (
        Index('idx_signature_index', 'signature', 'index'),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='ID')
    signature = Column(String(128), nullable=False, comment='回測簽名')
    index = Column(Integer, nullable=False, comment='索引')

    date = Column(String(64), nullable=False, comment='時間')
    action = Column(String(10))
    stock_id = Column(String(32), primary_key=True, nullable=False, comment='股票 ID')
    shares = Column(Integer, nullable=False, comment='股')
    price = Column(Numeric(precision=10, scale=4), nullable=False, comment='價格')
    fee = Column(Integer, nullable=False, comment='手續費')
    amount = Column(Integer, nullable=False, comment='金額')
    note = Column(String(32), nullable=False, comment='備註')

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
