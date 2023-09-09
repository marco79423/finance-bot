import pandas as pd

from finance_bot.core.tw_stock import TWStockCore
from finance_bot.infrastructure import infra
from .base import ServiceBase


class TWStockService(ServiceBase):
    name = 'tw_stock'

    def __init__(self, app):
        super().__init__(app)
        self.tw_stock_bot = TWStockCore()

    def set_schedules(self):
        infra.scheduler.add_schedule_task(
            self.execute_schedule_update_task,
            schedule_conf_key='tw_stock.schedule.schedule_update_task',
        )

    async def execute_schedule_update_task(self):
        today = pd.Timestamp.today().normalize()

        await self.execute_task(self.tw_stock_bot.update_stocks, success_message='台灣股票資訊更新完畢',
                                error_message='台灣股票資訊更新失敗', retries=5)

        yesterday = today - pd.Timedelta(days=1)
        await self.execute_task(self.tw_stock_bot.update_prices_for_date, kargs={'date': yesterday},
                                success_message='{date:%Y-%m-%d} 股價更新完畢',
                                error_message='{date:%Y-%m-%d} 股價更新失敗 [{retry_count}]', retries=5)

        # 根據規定上市櫃公司營收必須在次月的10號前公告，但遇假期可以延期，如 10 號是週六，可以等下週一才公布
        # 但我想每天都抓應該也不會怎樣
        last_month = today - pd.DateOffset(months=1)
        await self.execute_task(self.tw_stock_bot.update_monthly_revenue,
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
            self.tw_stock_bot.update_all_financial_statements_by_quarter,
            kargs={'year': last_period.year, 'quarter': last_period.quarter},
            success_message='{year}Q{quarter} 財報更新完畢',
            error_message='{year}Q{quarter} 財報更新失敗'
        )

        # await self.execute_task(
        #     self.tw_stock_bot.data.rebuild_cache,
        #     success_message='台股資料快取完畢',
        #     error_message='台股資料快取失敗'
        # )

    async def update_stocks(self):
        await self.execute_task(self.tw_stock_bot.update_stocks, success_message='台灣股票資訊更新完畢',
                                error_message='台灣股票資訊更新失敗')

    async def update_prices_for_date_range(self, start, end):
        await self.execute_task(self.tw_stock_bot.update_prices_for_date_range, kargs={'start': start, 'end': end},
                                success_message='{start} ~ {end} 股價更新完畢',
                                error_message='{start} ~ {end} 股價更新失敗')

    async def update_monthly_revenue(self, year, month):
        await self.execute_task(self.tw_stock_bot.update_monthly_revenue, kargs={'year': year, 'month': month},
                                success_message='{year}-{month} 月營收財報更新完畢',
                                error_message='{year}-{month} 月營收財報更新失敗')

    async def update_financial_statements(self, stock_id=None, year=None, quarter=None, force_update_db=False):
        if stock_id and year and quarter:
            await self.execute_task(self.tw_stock_bot.update_financial_statements_for_stock_by_quarter,
                                    kargs={'stock_id': stock_id, 'year': year, 'quarter': quarter},
                                    success_message='{stock_id} 的 {year}Q{quarter} 財報更新完畢',
                                    error_message='{stock_id} 的 {year}Q{quarter} 財報更新失敗')
        elif stock_id and not year and not quarter:
            await self.execute_task(self.tw_stock_bot.update_all_financial_statements_for_stock_id,
                                    kargs={'stock_id': stock_id, 'force_update_db': force_update_db},
                                    success_message='{stock_id} 的財報更新完畢',
                                    error_message='{stock_id} 的財報更新失敗')
        elif not stock_id and year and quarter:
            await self.execute_task(self.tw_stock_bot.update_all_financial_statements_by_quarter,
                                    kargs={'year': year, 'quarter': quarter},
                                    success_message='{year}Q{quarter} 財報更新完畢',
                                    error_message='{year}Q{quarter} 財報更新失敗')
        elif not stock_id and not year and not quarter:
            await self.execute_task(self.tw_stock_bot.update_all_financial_statements,
                                    kargs={'force_update_db': force_update_db},
                                    success_message='所有財報更新完畢', error_message='所有財報更新失敗')
        else:
            raise ValueError('不支援的操作')
