from sqlalchemy import create_engine

from finance_bot.ticker_db.model.base import Base
from finance_bot.utility import get_project_folder


def get_engine():
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
