from sqlalchemy import create_engine

from finance_bot.config import conf
from finance_bot.tw_stock.ticker_db.model.base import Base
from finance_bot.utility import get_project_folder


def get_engine():
    engine = create_engine(
        conf.tw_stock.database.url,
        pool_recycle=3600,  # 多少時間自動重連 (MySQL 預設會 8 小時踢人)
    )

    # 自動進行 Migrate
    migrate(engine)

    return engine


def get_sqlite3_engine():
    """Deprecated: 請改用 get_engine"""
    db_path = get_data_db_path()
    engine = create_engine(f'sqlite:///{db_path}')

    # 自動進行 Migrate
    migrate(engine)

    return engine


def get_data_db_path():
    data_folder = get_project_folder() / 'data'
    if not data_folder.exists():
        data_folder.mkdir()
    return data_folder / 'ticker.db'


def migrate(engine):
    Base.metadata.create_all(bind=engine)
