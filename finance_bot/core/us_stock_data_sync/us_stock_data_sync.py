import pandas as pd
import uvicorn

from finance_bot.core.base import CoreBase
from finance_bot.core.us_stock_data_sync.updater import USStockUpdater
from finance_bot.infrastructure import infra


class USStockDataSync(CoreBase):
    name = 'us_stock_data_sync'

    def __init__(self):
        super().__init__()
        self.updater = USStockUpdater(logger=self.logger)

    def start(self):
        self.logger.info(f'啟動 {self.name} ...')
        app = self.get_app()

        @app.on_event("startup")
        async def startup():
            await self.listen()

        uvicorn.run(app, host='0.0.0.0', port=16960)

    async def listen(self):
        await infra.mq.subscribe('us_stock_data_sync.update_us_stock', self._update_us_stock_handler)
        await infra.mq.subscribe('us_stock_data_sync.update_us_stock_prices', self._update_us_stock_prices_handler)
        await infra.mq.subscribe('us_stock_data_sync.update_db_cache', self._update_db_cache_handler)

    async def _update_us_stock_handler(self, sub, data):
        await self.execute_task(
            '美國股票資訊更新',
            'us_stock_data_sync.update_us_stock',
            self.updater.update_stocks,
            retries=5,
        )

    async def _update_us_stock_prices_handler(self, sub, data):
        today = pd.Timestamp(infra.time.get_now()).normalize()
        yesterday = today - pd.Timedelta(days=1)

        await self.execute_task(
            f'{yesterday:%Y-%m-%d} 股價資訊更新',
            'us_stock_data_sync.update_us_stock_prices',
            self.updater.update_prices_for_date,
            kargs=dict(date=yesterday),
            retries=5,
        )

    async def _update_db_cache_handler(self, sub, data):
        await self.execute_task(
            f'美股資料快取更新',
            'us_stock_data_sync.update_db_cache',
            self.updater.rebuild_cache,
            retries=5,
        )


if __name__ == '__main__':
    def main():
        bot = USStockDataSync()
        # bot.update_stocks()
        # bot.update_prices_for_date_range('2004-01-01', '2022-02-14')


    main()
