import pathlib

from finance_bot.infrastructure.base import ManagerBase


class PathManager(ManagerBase):

    @property
    def project_folder(self):
        return pathlib.Path(__file__).resolve().parent.parent.parent

    @property
    def data_folder(self):
        data_folder = self.project_folder / 'data'
        data_folder.mkdir(exist_ok=True)
        return data_folder

    @property
    def logs_folder(self):
        data_folder = self.project_folder / 'logs'
        data_folder.mkdir(exist_ok=True)
        return data_folder
