import pandas as pd

from finance_bot.core import DataSync
from finance_bot.infrastructure import infra
from .base import ServiceBase


class DataSyncService(ServiceBase):
    name = 'data_sync'

    def __init__(self, app):
        super().__init__(app)
        self.data_sync = DataSync()

    def set_schedules(self):
        infra.scheduler.add_schedule_task(
            self.execute_schedule_update_task,
            schedule_conf_key='server.service.data_sync.schedule.schedule_update_task',
        )

    async def execute_schedule_update_task(self):
        today = pd.Timestamp.today().normalize()

        await self.execute_task(self.data_sync.update_stocks, success_message='台灣股票資訊更新完畢',
                                error_message='台灣股票資訊更新失敗', retries=5)

        yesterday = today - pd.Timedelta(days=1)
        await self.execute_task(self.data_sync.update_prices_for_date, kargs={'date': yesterday},
                                success_message='{date:%Y-%m-%d} 股價更新完畢',
                                error_message='{date:%Y-%m-%d} 股價更新失敗 [{retry_count}]', retries=5)

        # 根據規定上市櫃公司營收必須在次月的10號前公告，但遇假期可以延期，如 10 號是週六，可以等下週一才公布
        # 但我想每天都抓應該也不會怎樣
        last_month = today - pd.DateOffset(months=1)
        await self.execute_task(self.data_sync.update_monthly_revenue,
                                kargs={'year': last_month.year, 'month': last_month.month},
                                success_message='{year}-{month} 月營收財報更新完畢',
                                error_message='{year}-{month} 月營收財報更新失敗')

        # 財報公布： 一般公司
        # * 第一季（Q1）法說會：5/15 前
        # * 第二季（Q2）財報：8/14 前
        # * 第三季（Q3）財報：11/14 前
        # * 第四季（Q4）財報及年報：隔年 3/31 前
        #
        # 財報公布： 金融業
        # * 第一季（Q1）財報：5/15 前
        # * 第二季（Q2）財報：8/31 前
        # * 第三季（Q3）財報：11/14 前
        last_period = pd.Period(pd.Timestamp.now(), freq='Q') - 1
        await self.execute_task(
            self.data_sync.update_all_financial_statements_by_quarter,
            kargs={'year': last_period.year, 'quarter': last_period.quarter},
            success_message='{year}Q{quarter} 財報更新完畢',
            error_message='{year}Q{quarter} 財報更新失敗'
        )

        # await self.execute_task(
        #     self.tw_stock_bot.data.rebuild_cache,
        #     success_message='台股資料快取完畢',
        #     error_message='台股資料快取失敗'
        # )
