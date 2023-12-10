from sqlalchemy import Column, String, DateTime, func, Text, Boolean

from .base import Base


class TaskStatus(Base):
    __tablename__ = 'task_status'

    key = Column(String(128), primary_key=True, comment='任務 Key')
    is_error = Column(Boolean, nullable=False, default=True, comment='是否出錯')
    detail = Column(Text, default='', comment='內容')

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
