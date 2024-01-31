import pandas as pd
import uvicorn

from finance_bot.core.base import CoreBase
from finance_bot.core.tw_stock_data_sync.updater import TWStockUpdater
from finance_bot.infrastructure import infra


class TWStockDataSync(CoreBase):
    name = 'tw_stock_data_sync'

    def __init__(self):
        super().__init__()
        self.updater = TWStockUpdater(logger=self.logger)

    def start(self):
        self.logger.info(f'啟動 {self.name} ...')
        app = self.get_app()

        @app.on_event("startup")
        async def startup():
            await self.listen()

        uvicorn.run(app, host='0.0.0.0', port=16920)

    async def listen(self):
        await infra.mq.subscribe('tw_stock_data_sync.update_tw_stock', self._update_tw_stock_handler)
        await infra.mq.subscribe('tw_stock_data_sync.update_tw_stock_prices', self._update_tw_stock_prices_handler)
        await infra.mq.subscribe('tw_stock_data_sync.update_monthly_revenue', self._update_monthly_revenue_handler)
        await infra.mq.subscribe('tw_stock_data_sync.update_financial_statements', self._update_financial_statements_handler)
        await infra.mq.subscribe('tw_stock_data_sync.update_db_cache', self._update_db_cache_handler)

    async def _update_tw_stock_handler(self, sub, data):
        await self.execute_task(
            '台灣股票資訊更新',
            'tw_stock_data_sync.update_tw_stock',
            self.updater.update_stocks,
            retries=5,
        )

    async def _update_tw_stock_prices_handler(self, sub, data):
        today = pd.Timestamp(infra.time.get_now()).normalize()
        yesterday = today - pd.Timedelta(days=1)

        await self.execute_task(
            f'{yesterday:%Y-%m-%d} 股價資訊更新',
            'tw_stock_data_sync.update_tw_stock_prices',
            self.updater.update_prices_for_date,
            kargs=dict(date=yesterday),
            retries=5,
        )

    async def _update_monthly_revenue_handler(self, sub, data):
        # 根據規定上市櫃公司營收必須在次月的10號前公告，但遇假期可以延期，如 10 號是週六，可以等下週一才公布
        # 但我想每天都抓應該也不會怎樣
        today = pd.Timestamp(infra.time.get_now()).normalize()

        # 上個月的同一天
        target_date = today - pd.DateOffset(months=1)
        year, month = target_date.year, target_date.month

        await self.execute_task(
            f'{year}-{month} 月營收財報更新',
            'tw_stock_data_sync.update_monthly_revenue',
            self.updater.update_monthly_revenue,
            kargs=dict(year=year, month=month),
            retries=5,
        )

    async def _update_financial_statements_handler(self, sub, data):
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

        last_period = pd.Period(pd.Timestamp(infra.time.get_now()), freq='Q') - 1
        year, quarter = last_period.year, last_period.quarter
        await self.execute_task(
            f'{year}Q{quarter} 財報更新',
            'tw_stock_data_sync.update_financial_statements',
            self.updater.update_all_financial_statements_by_quarter,
            kargs=dict(year=year, quarter=quarter),
            retries=5,
        )

    async def _update_db_cache_handler(self, sub, data):
        await self.execute_task(
            f'台股資料快取更新',
            'tw_stock_data_sync.update_db_cache',
            self.updater.rebuild_cache,
            retries=5,
        )


if __name__ == '__main__':
    def main():
        bot = TWStockDataSync()
        # bot.update_stocks()
        # bot.update_prices_for_date_range('2004-01-01', '2022-02-14')
        # for d in pd.date_range('2014-07', '2023-07', freq='MS'):
        #     print(f'{d.year}-{d.month:02}')
        #     bot.update_monthly_revenue(year=d.year, month=d.month)
        #     time.sleep(30)
        bot.updater.update_all_financial_statements_for_stock_id('2330')
        bot.updater.update_all_financial_statements_by_quarter(2022, 1)


    main()
