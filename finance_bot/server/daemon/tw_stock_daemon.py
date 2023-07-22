import pandas as pd
import pytz
import telegram
from apscheduler.triggers.cron import CronTrigger
from omegaconf import ListConfig

from finance_bot.config import conf, select_conf
from finance_bot.server.daemon.base import DaemonBase
from finance_bot.tw_stock.tw_stock_bot import TWStockBot


class TWStockDaemon(DaemonBase):

    def __init__(self, app):
        super().__init__(app)
        self.tw_stock_bot = TWStockBot(logger=self.logger)
        self.telegram_bot = telegram.Bot(conf.notification.telegram.token)

    def start(self):
        update_prices_task_schedule = select_conf('tw_stock.schedule.update_prices_task')
        if update_prices_task_schedule:
            if not isinstance(update_prices_task_schedule, ListConfig):
                update_prices_task_schedule = [update_prices_task_schedule]
            for schedule in update_prices_task_schedule:
                self.scheduler.add_job(
                    self.execute_update_prices_task,
                    CronTrigger.from_crontab(
                        schedule, timezone=pytz.timezone(conf.server.timezone),
                    ),
                )

    async def execute_update_prices_task(self):
        yesterday = pd.Timestamp.today().normalize() - pd.Timedelta(days=1)
        await self.tw_stock_bot.update_prices_for_date(yesterday)
        await self.telegram_bot.send_message(
            chat_id=conf.notification.telegram.chat_id,
            text=f'{yesterday::%Y-%m-%d} 股價更新完畢'
        )

    async def update_prices_for_date_range(self, start, end):
        try:
            self.tw_stock_bot.update_prices_for_date_range(start, end)
            await self.telegram_bot.send_message(
                chat_id=conf.notification.telegram.chat_id,
                text=f'{start} ~ {end} 股價更新完畢'
            )
        except Exception as e:
            await self.telegram_bot.send_message(
                chat_id=conf.notification.telegram.chat_id,
                text=f'{start} ~ {end} 股價更新失敗\n{str(e)}'
            )
