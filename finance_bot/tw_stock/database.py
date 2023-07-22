from sqlalchemy import create_engine

from finance_bot.config import conf
from .model.base import Base


def get_engine():
    engine = create_engine(
        conf.tw_stock.database.url,
        pool_recycle=3600,  # 多少時間自動重連 (MySQL 預設會 8 小時踢人)
    )

    # 自動進行 Migrate
    migrate(engine)

    return engine


def migrate(engine):
    Base.metadata.create_all(bind=engine)
