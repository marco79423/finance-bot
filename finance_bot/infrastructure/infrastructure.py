import logging
import pathlib
import sys

import pytz
from loguru import logger
from omegaconf import OmegaConf

from finance_bot.infrastructure.manager import ScheduleManager, TimeManager, DatabaseManager, DatabaseCacheManager, \
    NotifierManager, APIManager, PathManager

# 預設設定檔
DEFAULT_CONFIG = {

}


class Infrastructure:

    def __init__(self):
        self._conf = None
        self._logger = None
        self._schedule_manager = None
        self._time_manager = None
        self._database_manager = None
        self._database_cache_manager = None
        self._notifier_manager = None
        self._api_manager = None
        self._path_manager = None

    def start(self):
        pass

    @property
    def conf(self):
        if self._conf is None:
            config = OmegaConf.create(DEFAULT_CONFIG)

            project_folder = self.path.project_folder
            config_file = project_folder / 'conf.d' / 'config.yml'
            if not pathlib.Path(config_file).exists():
                raise ValueError('找不到設定檔 conf.d/config.yml')
            config.merge_with(OmegaConf.load(config_file))
            OmegaConf.set_readonly(config, True)
            self._conf = config
        return self._conf

    @property
    def scheduler(self) -> ScheduleManager:
        if self._schedule_manager is None:
            self._schedule_manager = ScheduleManager(self)
            self._schedule_manager.start()
        return self._schedule_manager

    @property
    def logger(self) -> logging.Logger:
        if self._logger is None:
            error_format = '[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>][<level>{level: <5}</level>][{extra[name]}][<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>] {message}'
            msg_format = '[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>][<level>{level: <5}</level>][{extra[name]}] {message}'

            def fix_timezone(record):
                tzinfo = pytz.timezone(self.conf.infrastructure.timezone)
                record["time"] = record["time"].replace(tzinfo=tzinfo)

            logger.configure(
                handlers=[
                    {
                        'sink': sys.stdout,
                        'level': 'INFO',
                        'format': msg_format,
                    },
                    {
                        'sink': self.path.logs_folder / '{time:%Y-%m-%d}.log',
                        'level': 'DEBUG',
                        'format': msg_format,
                        'rotation': '00:00',
                        'retention': '30 days',
                    },
                    {
                        'sink': self.path.logs_folder / '{time:%Y-%m-%d}-error.log',
                        'level': 'ERROR',
                        'format': error_format,
                        'rotation': '00:00',
                        'retention': '30 days',
                    },
                ],
                patcher=fix_timezone,
            )
            self._logger = logger
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
    def db_cache(self) -> DatabaseCacheManager:
        if self._database_cache_manager is None:
            self._database_cache_manager = DatabaseCacheManager(self)
            self._database_cache_manager.start()
        return self._database_cache_manager

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

    @property
    def path(self) -> PathManager:
        if self._path_manager is None:
            self._path_manager = PathManager(self)
            self._path_manager.start()
        return self._path_manager

    def select_conf(self, key):
        return OmegaConf.select(self.conf, key)
