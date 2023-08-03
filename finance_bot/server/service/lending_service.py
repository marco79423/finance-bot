import pytz
from apscheduler.triggers.cron import CronTrigger
from omegaconf import ListConfig

from finance_bot.bot.lending import LendingBot
from finance_bot.infrastructure import infra
from finance_bot.server.service.base import ServiceBase


class LendingService(ServiceBase):
    name = 'lending'

    def __init__(self, app):
        super().__init__(app)
        self.lending_bot = LendingBot()

    def set_schedules(self):
        lending_task_schedule = infra.select_conf('lending.schedule.lending_task')
        if lending_task_schedule:
            if not isinstance(lending_task_schedule, ListConfig):
                lending_task_schedule = [lending_task_schedule]

            for schedule in lending_task_schedule:
                infra.scheduler.add_job(
                    self.execute_lending_task,
                    CronTrigger.from_crontab(schedule, timezone=pytz.timezone(infra.conf.server.timezone)),
                    max_instances=1
                )

        sending_stats_schedule = infra.select_conf('lending.schedule.sending_stats')
        if sending_stats_schedule:
            if not isinstance(sending_stats_schedule, ListConfig):
                sending_stats_schedule = [sending_stats_schedule]

            for schedule in sending_stats_schedule:
                infra.scheduler.add_job(
                    self.send_stats,
                    CronTrigger.from_crontab(schedule, timezone=pytz.timezone(infra.conf.server.timezone)),
                    max_instances=1,
                    misfire_grace_time=60 * 5
                )

    async def execute_lending_task(self):
        await self.execute_task(
            self.lending_bot.execute_lending_task,
            error_message='借錢任務執行失敗\n{error}',
        )

    async def get_lending_records(self):
        return await self.lending_bot.get_lending_records()

    async def send_stats(self):
        async def get_stats_msg():
            stats = await self.lending_bot.get_stats()
            return {
                'lending_amount': round(stats.lending_amount, 2),
                'daily_earn': round(stats.daily_earn, 2),
                'average_rate': round(stats.average_rate * 100, 6),
            }

        await self.execute_task(
            get_stats_msg,
            success_message='總借出: {lending_amount:.2f}\n預估日收益: {daily_earn:.2f} (平均利率: {average_rate:.6f}%)',
            error_message='計算統計執行失敗 [{retry_count}]\n{error}',
            retries=5
        )
