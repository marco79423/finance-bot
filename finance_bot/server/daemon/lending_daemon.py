import pytz
import telegram
from apscheduler.triggers.cron import CronTrigger
from omegaconf import ListConfig

from finance_bot.config import conf, select_conf
from finance_bot.lending.lending_bot import LendingBot
from finance_bot.server.daemon.base import DaemonBase


class LendingDaemon(DaemonBase):

    def __init__(self, app):
        super().__init__(app)
        self.lending_bot = LendingBot(logger=self.logger)
        self.telegram_bot = telegram.Bot(conf.notification.telegram.token)

    def start(self):
        lending_task_schedule = select_conf('lending.schedule.lending_task')
        if lending_task_schedule:
            if not isinstance(lending_task_schedule, ListConfig):
                lending_task_schedule = [lending_task_schedule]
            for schedule in lending_task_schedule:
                self.scheduler.add_job(
                    self.execute_lending_task,
                    CronTrigger.from_crontab(
                        schedule, timezone=pytz.timezone(conf.server.timezone),
                    ),
                )

        sending_stats_schedule = select_conf('lending.schedule.sending_stats')
        if sending_stats_schedule:
            if not isinstance(sending_stats_schedule, ListConfig):
                sending_stats_schedule = [sending_stats_schedule]
            for schedule in sending_stats_schedule:
                self.scheduler.add_job(
                    self.send_stats,
                    CronTrigger.from_crontab(
                        schedule, timezone=pytz.timezone(conf.server.timezone)
                    ),
                )

    async def get_lending_records(self):
        return await self.lending_bot.get_lending_records()

    async def execute_lending_task(self):
        await self.lending_bot.execute_lending_task()

    async def send_stats(self):
        stats = await self.lending_bot.get_stats()
        await self.telegram_bot.send_message(
            chat_id=conf.notification.telegram.chat_id,
            text='總借出: {lending_amount:.2f}\n預估日收益: {daily_earn:.2f} (平均利率: {average_rate:.6f}%)'.format(
                lending_amount=round(stats.lending_amount, 2),
                daily_earn=round(stats.daily_earn, 2),
                average_rate=round(stats.average_rate * 100, 6),
            )
        )