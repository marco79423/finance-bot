import uvicorn

from finance_bot.core.base import CoreBase
from finance_bot.infrastructure import infra


class Schedule(CoreBase):
    name = 'schedule'

    def start(self):
        self.logger.info(f'啟動 {self.name} ...')

        app = self.get_app()

        @app.on_event("startup")
        async def startup():
            await self.start_jobs()

        uvicorn.run(app, host='0.0.0.0', port=16930)

    async def start_jobs(self):
        infra.scheduler.add_schedule_task(
            self.create_task('data_sync.schedule_update'),
            schedule_conf_key='core.schedule.data_sync.schedule_update',
        )
        infra.scheduler.add_schedule_task(
            self.create_task('crypto_loan.lending_task'),
            schedule_conf_key='core.schedule.crypto_loan.lending_task',
        )
        infra.scheduler.add_schedule_task(
            self.create_task('super_bot.daily_status'),
            schedule_conf_key='core.schedule.super_bot.daily_status',
            misfire_grace_time=60 * 5
        )

    @staticmethod
    def create_task(topic):
        async def send_task():
            await infra.mq.publish(topic, {})

        return send_task
