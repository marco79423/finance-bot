from pathlib import Path

from aiopath import AsyncPath

from finance_bot.infrastructure.manager.base import ManagerBase


class PathManager(ManagerBase):

    @property
    def project_folder(self):
        return AsyncPath(Path(__file__).resolve().parent.parent.parent.parent)

    @property
    def config_folder(self):
        return self.project_folder / 'conf.d'

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
        db_cache_folder = self.data_folder / 'cache'
        Path(db_cache_folder).mkdir(exist_ok=True)
        return db_cache_folder

    @property
    def multicharts_folder(self):
        multicharts_folder = self.data_folder / 'multicharts'
        Path(multicharts_folder).mkdir(exist_ok=True)
        return multicharts_folder
