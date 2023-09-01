from pathlib import Path

from aiopath import AsyncPath

from finance_bot.infrastructure.base import ManagerBase


class PathManager(ManagerBase):

    @property
    def project_folder(self):
        return AsyncPath(Path(__file__).resolve().parent.parent.parent)

    @property
    def data_folder(self):
        data_folder = self.project_folder / 'data'
        Path(data_folder).mkdir(exist_ok=True)
        return data_folder

    @property
    def logs_folder(self):
        log_folder = self.project_folder / 'logs'
        Path(log_folder).mkdir(exist_ok=True)
        return log_folder

    @property
    def db_cache_folder(self):
        db_cache_folder = self.project_folder / 'db_cache'
        Path(db_cache_folder).mkdir(exist_ok=True)
        return db_cache_folder
