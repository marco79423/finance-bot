import asyncio

import pandas as pd
import pytz
import telegram
from apscheduler.triggers.cron import CronTrigger
from omegaconf import ListConfig

from finance_bot.config import conf, select_conf
from finance_bot.server.service.base import ServiceBase
from finance_bot.tw_stock.tw_stock_bot import TWStockBot


class TWStockService(ServiceBase):
    name = 'tw-stock'

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
        for i in range(5):
            try:
                self.tw_stock_bot.update_stocks()
                await self.telegram_bot.send_message(
                    chat_id=conf.notification.telegram.chat_id,
                    text=f'台灣股票資訊更新完畢'
                )
                return
            except Exception as e:
                await self.telegram_bot.send_message(
                    chat_id=conf.notification.telegram.chat_id,
                    text=f'台灣股票資訊更新失敗 [{i + 1} 次]\n{str(e)}'
                )
                await asyncio.sleep(60)

        for i in range(5):
            yesterday = pd.Timestamp.today().normalize() - pd.Timedelta(days=1)
            try:
                self.tw_stock_bot.update_prices_for_date(yesterday)
                await self.telegram_bot.send_message(
                    chat_id=conf.notification.telegram.chat_id,
                    text=f'{yesterday::%Y-%m-%d} 股價更新完畢'
                )
                return
            except Exception as e:
                await self.telegram_bot.send_message(
                    chat_id=conf.notification.telegram.chat_id,
                    text=f'{yesterday::%Y-%m-%d} 股價更新失敗 [{i + 1} 次]\n{str(e)}'
                )
                await asyncio.sleep(60)

    async def update_prices_for_date_range(self, start, end):
        for i in range(5):
            try:
                self.tw_stock_bot.update_prices_for_date_range(start, end)
                await self.telegram_bot.send_message(
                    chat_id=conf.notification.telegram.chat_id,
                    text=f'{start} ~ {end} 股價更新完畢'
                )
                return
            except Exception as e:
                await self.telegram_bot.send_message(
                    chat_id=conf.notification.telegram.chat_id,
                    text=f'{start} ~ {end} 股價更新失敗\n{str(e)}'
                )
