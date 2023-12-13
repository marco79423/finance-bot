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

    async def start_jobs(self):
        # crypto loan
        infra.scheduler.add_schedule_task(
            self.create_task('crypto_loan.update_status'),
            schedule_conf_key='core.schedule.crypto_loan.update_status',
        )

        # data_sync
        infra.scheduler.add_schedule_task(
            self.create_task('data_sync.update_tw_stock'),
            schedule_conf_key='core.schedule.data_sync.update_tw_stock',
        )
        infra.scheduler.add_schedule_task(
            self.create_task('data_sync.update_tw_stock_prices'),
            schedule_conf_key='core.schedule.data_sync.update_tw_stock_prices',
        )
        infra.scheduler.add_schedule_task(
            self.create_task('data_sync.update_monthly_revenue'),
            schedule_conf_key='core.schedule.data_sync.update_monthly_revenue',
        )
        infra.scheduler.add_schedule_task(
            self.create_task('data_sync.update_financial_statements'),
            schedule_conf_key='core.schedule.data_sync.update_financial_statements',
        )
        infra.scheduler.add_schedule_task(
            self.create_task('data_sync.update_db_cache'),
            schedule_conf_key='core.schedule.data_sync.update_db_cache',
        )

        # tw_stock_trade
        infra.scheduler.add_schedule_task(
            self.create_task('tw_stock_trade.update_strategy_actions'),
            schedule_conf_key='core.schedule.tw_stock_trade.update_strategy_actions',
        )

        # super_bot
        infra.scheduler.add_schedule_task(
            self.create_task('super_bot.send_daily_status'),
            schedule_conf_key='core.schedule.super_bot.send_daily_status',
        )

    @staticmethod
    def create_task(topic):
        async def send_task():
            await infra.mq.publish(topic, {})

        return send_task
