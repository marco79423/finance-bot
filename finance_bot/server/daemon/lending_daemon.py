import asyncio

import pytz
import telegram
from apscheduler.triggers.combining import OrTrigger
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
            self.scheduler.add_job(
                self.execute_lending_task,
                OrTrigger(
                    CronTrigger.from_crontab(schedule, timezone=pytz.timezone(conf.server.timezone))
                    for schedule in lending_task_schedule
                ),
                max_instances=1
            )

        sending_stats_schedule = select_conf('lending.schedule.sending_stats')
        if sending_stats_schedule:
            if not isinstance(sending_stats_schedule, ListConfig):
                sending_stats_schedule = [sending_stats_schedule]

            self.scheduler.add_job(
                self.send_stats,
                OrTrigger(
                    CronTrigger.from_crontab(schedule, timezone=pytz.timezone(conf.server.timezone))
                    for schedule in sending_stats_schedule
                ),
                max_instances=1,
                misfire_grace_time=60 * 5
            )

    async def get_lending_records(self):
        return await self.lending_bot.get_lending_records()

    async def execute_lending_task(self):
        try:
            await self.lending_bot.execute_lending_task()
        except Exception as e:
            self.logger.error(f'execute_lending_task 執行失敗: {str(e)}')

    async def send_stats(self):
        for i in range(5):
            try:
                stats = await self.lending_bot.get_stats()
                await self.telegram_bot.send_message(
                    chat_id=conf.notification.telegram.chat_id,
                    text='總借出: {lending_amount:.2f}\n預估日收益: {daily_earn:.2f} (平均利率: {average_rate:.6f}%)'.format(
                        lending_amount=round(stats.lending_amount, 2),
                        daily_earn=round(stats.daily_earn, 2),
                        average_rate=round(stats.average_rate * 100, 6),
                    )
                )
            except Exception as e:
                await self.telegram_bot.send_message(
                    chat_id=conf.notification.telegram.chat_id,
                    text=f'計算統計失敗 [{i + 1} 次]\n{str(e)}'
                )
                await asyncio.sleep(60)
