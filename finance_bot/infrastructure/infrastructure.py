import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from omegaconf import OmegaConf

from .api_manager import APIManager
from .database_manager import DatabaseManager
from .notifier_manager import NotifierManager
from .time_manager import TimeManager
from ..config import conf


class Infrastructure:

    def __init__(self):
        self.conf = conf

        self._logger = None
        self._scheduler = None
        self._time_manager = None
        self._database_manager = None
        self._notifier_manager = None
        self._api_manager = None

    def start(self):
        pass

    @property
    def scheduler(self) -> AsyncIOScheduler:
        if self._scheduler is None:
            self._scheduler = AsyncIOScheduler(logger=self.logger.getChild('scheduler'))
            self._scheduler.start()
        return self._scheduler

    @property
    def logger(self) -> logging.Logger:
        if self._logger is None:
            # 設定環境
            logging.basicConfig(
                level=logging.INFO,
                datefmt='%Y-%m-%d %H:%M:%S',
                format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
            )
            logging.Formatter.converter = lambda *args: self.time.get_now().timetuple()
            logging.getLogger('apscheduler').setLevel(logging.WARN)
            self._logger = logging.getLogger()
        return self._logger

    @property
    def time(self) -> TimeManager:
        if self._time_manager is None:
            self._time_manager = TimeManager(self)
            self._time_manager.start()
        return self._time_manager

    @property
    def db(self) -> DatabaseManager:
        if self._database_manager is None:
            self._database_manager = DatabaseManager(self)
            self._database_manager.start()
        return self._database_manager

    @property
    def notifier(self) -> NotifierManager:
        if self._notifier_manager is None:
            self._notifier_manager = NotifierManager(self)
            self._notifier_manager.start()
        return self._notifier_manager

    @property
    def api(self) -> APIManager:
        if self._api_manager is None:
            self._api_manager = APIManager(self)
            self._api_manager.start()
        return self._api_manager

    def select_conf(self, key):
        return OmegaConf.select(self.conf, key)
