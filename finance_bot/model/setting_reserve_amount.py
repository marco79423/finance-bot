from sqlalchemy import Column, String, Index, DateTime, func, Numeric

from .base import Base


class SettingReserveAmount(Base):
    __tablename__ = 'setting_reserve_amount'
    __table_args__ = (
        Index('idx_name', 'name'),
    )

    key = Column(String(60), primary_key=True, nullable=False, comment='Key')
    name = Column(String(60), nullable=False, comment='名稱')
    amount = Column(Numeric(precision=38, scale=18), nullable=False, default=0, comment='金額')

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
