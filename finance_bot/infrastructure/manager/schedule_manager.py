import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from omegaconf import ListConfig

from finance_bot.infrastructure.manager.base import ManagerBase


class ScheduleManager(ManagerBase):

    def __init__(self, infra):
        super().__init__(infra)
        self._scheduler = AsyncIOScheduler()

    def start(self):
        self._scheduler.start()

    @property
    def jobs(self):
        return self._scheduler.get_jobs()

    def add_task(self, task, *args, **kargs):
        self._scheduler.add_job(
            task,
            *args,
            max_instances=1,
            **kargs,
        )

    def add_schedule_task(self, task, schedule_conf_key, **kargs):
        schedules = self.select_conf_for_schedules(schedule_conf_key)
        if schedules:
            for schedule in schedules:
                self._scheduler.add_job(
                    task,
                    CronTrigger.from_crontab(schedule, timezone=pytz.timezone(self.conf.infrastructure.timezone)),
                    max_instances=1,
                    **kargs
                )

    def select_conf_for_schedules(self, key):
        schedules = self.infra.select_conf(key)
        if schedules:
            if not isinstance(schedules, ListConfig):
                schedules = [schedules]
        return schedules
