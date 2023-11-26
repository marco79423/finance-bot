from finance_bot.infrastructure import infra
from .base import ServiceBase


class ScheduleService(ServiceBase):
    name = 'schedule'

    def set_schedules(self):
        infra.scheduler.add_schedule_task(
            self.create_task('data_sync.schedule_update'),
            schedule_conf_key='server.service.data_sync.schedule.schedule_update_task',
        )
        infra.scheduler.add_schedule_task(
            self.create_task('crypto_loan.lending_task'),
            schedule_conf_key='server.service.crypto_loan.schedule.lending_task',
        )
        infra.scheduler.add_schedule_task(
            self.create_task('crypto_loan.send_stats'),
            schedule_conf_key='server.service.crypto_loan.schedule.sending_stats',
            misfire_grace_time=60 * 5
        )

    @staticmethod
    def create_task(topic):
        async def send_task():
            await infra.mq.publish(topic, {})

        return send_task
