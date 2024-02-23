from sqlalchemy import Column, String, Index, DateTime, func, Boolean

from .base import Base


class SettingControl(Base):
    __tablename__ = 'setting_control'
    __table_args__ = (
        Index('idx_name', 'name'),
    )

    key = Column(String(60), primary_key=True, nullable=False, comment='任務 Key')
    name = Column(String(60), nullable=False, comment='名稱')
    enabled = Column(Boolean, nullable=False, comment='啟動')

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
