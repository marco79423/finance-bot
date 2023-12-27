from sqlalchemy import Column, String, DateTime, func, Index, BigInteger, Integer
from sqlalchemy.dialects.mysql import LONGTEXT

from .base import Base


class TWStockBacktestResult(Base):
    __tablename__ = 'tw_stock_backtest_result'
    __table_args__ = (
        Index('idx_key', 'key'),
    )

    id = Column(BigInteger, primary_key=True, comment='回測 ID')
    key = Column(String(128), nullable=False, comment='回測參數雜湊')

    strategy_name = Column(String(10), comment='策略名稱')
    params = Column(LONGTEXT, nullable=False, comment='參數')
    init_balance = Column(Integer, nullable=False, comment='開始資金')
    final_balance = Column(Integer, nullable=False, comment='結束資金')
    start_time = Column(DateTime, nullable=False, comment='開始時間')
    end_time = Column(DateTime, nullable=False, comment='結束時間')
    trade_logs = Column(LONGTEXT, nullable=False, comment='交易紀錄')

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
