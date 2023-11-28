import asyncio

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
            infra.scheduler.add_schedule_task(
                self.create_task('data_sync.schedule_update'),
                schedule_conf_key='core.schedule.data_sync.schedule_update',
            )
            infra.scheduler.add_schedule_task(
                self.create_task('crypto_loan.lending_task'),
                schedule_conf_key='core.schedule.crypto_loan.lending_task',
            )
            infra.scheduler.add_schedule_task(
                self.create_task('crypto_loan.send_stats'),
                schedule_conf_key='core.schedule.crypto_loan.sending_stats',
                misfire_grace_time=60 * 5
            )

        uvicorn.run(app, host='0.0.0.0', port=16930)

        asyncio.get_running_loop().run_forever()

    @staticmethod
    def create_task(topic):
        async def send_task():
            await infra.mq.publish(topic, {})

        return send_task
