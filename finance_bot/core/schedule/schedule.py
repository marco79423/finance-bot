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

        @app.get('/jobs')
        async def get_jobs():
            return [str(job) for job in infra.scheduler.jobs]

        uvicorn.run(app, host='0.0.0.0', port=16930)

    tasks = [
        # crypto loan
        ('crypto_loan.update_status', 'core.schedule.crypto_loan.update_status'),
        # data_sync
        ('data_sync.update_tw_stock', 'core.schedule.data_sync.update_tw_stock'),
        ('data_sync.update_tw_stock_prices', 'core.schedule.data_sync.update_tw_stock_prices'),
        ('data_sync.update_monthly_revenue', 'core.schedule.data_sync.update_monthly_revenue'),
        ('data_sync.update_financial_statements', 'core.schedule.data_sync.update_financial_statements'),
        ('data_sync.update_db_cache', 'core.schedule.data_sync.update_db_cache'),
        # tw_stock_trade
        ('tw_stock_trade.update_strategy_actions', 'core.schedule.tw_stock_trade.update_strategy_actions'),
        # super_bot
        ('super_bot.send_daily_status', 'core.schedule.super_bot.send_daily_status'),
    ]

    async def start_jobs(self):
        for task_key, conf_key in self.tasks:
            infra.scheduler.add_schedule_task(
                self.create_task(task_key),
                schedule_conf_key=conf_key,
            )

    async def send_task(self, task_key):
        self.logger.info(f'開始發送任務 {task_key} ...')
        if task_key in (key for key, _ in self.tasks):
            self.logger.info(f'發送 {task_key} 至 MQ')
            await infra.mq.publish(task_key, {})

    @staticmethod
    def create_task(topic):
        async def send_task():
            await infra.mq.publish(topic, {})

        send_task.__name__ = f'send_task<{topic}>'

        return send_task
