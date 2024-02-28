import datetime as dt

import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from finance_bot.infrastructure import infra
from finance_bot.model import USStock


class USStockUpdater:
    COMMIT_GROUP_SIZE = 1000

    def __init__(self, logger):
        self.logger = logger

    async def update_stocks(self):
        self.logger.info(f'開始更新美國股票資訊 ...')
        df = await self.crawl_stocks()

        total_count = len(df)
        self.logger.info(f'取得 {total_count} 筆資訊')
        async with AsyncSession(infra.db.async_engine) as session:
            await infra.db.batch_insert_or_update(session, USStock, df)
        self.logger.info('美國股票資訊更新完成')
        return dict(total_count=total_count)

    async def update_prices_for_date(self, date=None):
        pass

    async def update_prices_for_date_range(self, start=None, end=None, random_delay=True):
        pass

    async def rebuild_cache(self):
        # us_stock
        self.logger.info(f'開始重建 us_stock 快取 ...')
        stock_df = pd.read_sql(
            sql=text("SELECT * FROM us_stock"),
            con=infra.db.engine,
            index_col='stock_id',
            parse_dates=['created_at', 'updated_at'],
        )
        infra.db_cache.save(key='us_stock', df=stock_df)

        # us_stock_price
        self.logger.info(f'開始重建 us_stock_price 快取 ...')
        prices_df = pd.read_sql(
            sql=text("SELECT * FROM us_stock_price"),
            con=infra.db.engine,
            index_col='date',
            parse_dates=['date'],
        )
        infra.db_cache.save(key='us_stock_price', df=prices_df)

    @staticmethod
    async def crawl_stocks():
        pass

    @staticmethod
    async def crawl_price(date: dt.datetime):
        pass

    @staticmethod
    def _get_df_value(df, possible_indexes, column_name='value'):
        value = None
        for possible_index in possible_indexes:
            if value is None:
                try:
                    value = df.at[possible_index, column_name]
                except KeyError:
                    pass
        return value
