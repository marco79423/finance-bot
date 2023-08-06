import pandas as pd

from finance_bot.bot.tw_stock.tw_stock_bot import TWStockBot
from finance_bot.infrastructure import infra
from finance_bot.server.service.base import ServiceBase


class TWStockService(ServiceBase):
    name = 'tw_stock'

    def __init__(self, app):
        super().__init__(app)
        self.tw_stock_bot = TWStockBot()

    def set_schedules(self):
        infra.scheduler.add_schedule_task(
            self.execute_schedule_update_task,
            schedule_conf_key='tw_stock.schedule.schedule_update_task',
        )

    async def execute_schedule_update_task(self):
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
            error_message='{start} ~ {end} 股價更新失敗',
        )

    async def update_monthly_revenue(self, year, month):
        await self.execute_task(
            self.tw_stock_bot.crawl_monthly_revenue,
            kargs={'year': year, 'month': month},
            success_message='{year}-{month} 月營收財報更新完畢',
            error_message='{year}-{month} 月營收財報更新失敗',
        )

    async def update_financial_statements(self, stock_id, year, season):
        await self.execute_task(
            self.tw_stock_bot.update_financial_statements,
            kargs={'stock_id': stock_id, 'year': year, 'season': season},
            success_message='{stock_id} 的 {year}Q{season} 財報更新完畢',
            error_message='{stock_id} 的 {year}Q{season} 財報更新失敗',
        )
