from sqlalchemy import Column, String, DateTime, func, BigInteger, Integer

from .base import Base


class TWStockAction(Base):
    __tablename__ = 'tw_stock_action'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='ID')
    operation = Column(String(32), comment='操作')
    stock_id = Column(String(32), primary_key=True, nullable=False, comment='股票 ID')
    shares = Column(Integer, nullable=False, comment='股')
    note = Column(String(32), nullable=False, comment='備註')

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
