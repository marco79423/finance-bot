import pandas as pd
import pytz
import telegram
from apscheduler.triggers.cron import CronTrigger
from finance_bot.config import conf, select_conf
from finance_bot.server.service.base import ServiceBase
from finance_bot.tw_stock.tw_stock_bot import TWStockBot
from omegaconf import ListConfig


class TWStockService(ServiceBase):
    name = 'tw_stock'

    def __init__(self, app):
        super().__init__(app)
        self.tw_stock_bot = TWStockBot(logger=self.logger)
        self.telegram_bot = telegram.Bot(conf.notification.telegram.token)

    def set_schedules(self):
        update_prices_task_schedule = select_conf('tw_stock.schedule.update_prices_task')
        if update_prices_task_schedule:
            if not isinstance(update_prices_task_schedule, ListConfig):
                update_prices_task_schedule = [update_prices_task_schedule]

            for schedule in update_prices_task_schedule:
                self.scheduler.add_job(
                    self.execute_update_prices_task,
                    CronTrigger.from_crontab(schedule, timezone=pytz.timezone(conf.server.timezone)),
                    max_instances=1,
                    misfire_grace_time=60 * 5
                )

    async def execute_update_prices_task(self):
        await self.execute_task(
            self.tw_stock_bot.update_stocks,
            success_message='台灣股票資訊更新完畢',
            error_message='台灣股票資訊更新失敗',
            retries=5,
        )

        yesterday = pd.Timestamp.today().normalize() - pd.Timedelta(days=1)
        await self.execute_task(
            self.tw_stock_bot.update_prices_for_date,
            kargs={'date': yesterday},
            success_message='{date:%Y-%m-%d} 股價更新完畢',
            error_message='{date:%Y-%m-%d} 股價更新失敗 [{retry_count}]\n{error}',
            retries=5,
        )

    async def update_prices_for_date_range(self, start, end):
        await self.execute_task(
            self.tw_stock_bot.update_prices_for_date_range,
            kargs={'start': start, 'end': end},
            success_message='{start} ~ {end} 股價更新完畢',
            error_message='{start} ~ {end} 股價更新失敗 [{retry_count}]\n{error}',
        )

    async def update_financial_statements(self, stock_id, year, season):
        await self.execute_task(
            self.tw_stock_bot.update_financial_statements,
            kargs={'stock_id': stock_id, 'year': year, 'season': season},
            success_message='{stock_id} 的 {year}Q{season} 財報更新完畢',
            error_message='{stock_id} 的 {year}Q{season} 財報更新失敗 [{retry_count}]\n{error}',
        )
