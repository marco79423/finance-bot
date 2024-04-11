import pandas as pd
import yfinance as yf
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from finance_bot.infrastructure import infra
from finance_bot.model import USStockPrice
from finance_bot.repository import USStockRepository


class USStockUpdater:
    COMMIT_GROUP_SIZE = 1000

    def __init__(self, logger):
        self.logger = logger
        self._us_stock_repo = USStockRepository()

    async def update_stocks(self):
        self.logger.info(f'開始更新美國股票資訊 ...')

        stock_df = pd.read_sql(
            sql=text("SELECT stock_id, tracked FROM us_stock"),
            con=infra.db.engine,
            index_col='stock_id',
        )

        tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]

        total_count = 0
        for stock_id in tickers['Symbol']:
            if stock_id in stock_df.index:
                continue

            ticker = yf.Ticker(stock_id)
            name = ticker.info['longName']
            async with AsyncSession(infra.db.async_engine) as session:
                await self._us_stock_repo.add(
                    session=session,
                    stock_id=stock_id,
                    name=name,
                )
                await session.commit()
            total_count += 1

        self.logger.info('美國股票資訊更新完成')
        return dict(total_count=total_count)

    async def update_prices_for_date(self, date=None):
        await self.update_prices_for_date_range(start=date, interval='1d')

    async def update_prices_for_date_range(self, start=None, end=None, interval=None):
        stock_df = pd.read_sql(
            sql=text("SELECT stock_id FROM us_stock WHERE tracked = 1"),
            con=infra.db.engine,
            index_col='stock_id',
        )

        for stock_id in stock_df.index:
            ticker = yf.Ticker(stock_id)
            df = ticker.history(start=start, end=end, interval=interval)
            if df.empty:
                continue

            df = df.reset_index()
            df = df.rename(columns={
                'Date': 'date',
                'Open': 'open',
                'Close': 'close',
                'High': 'high',
                'Low': 'low',
                'Volume': 'volume',
            })
            df['stock_id'] = stock_id
            df = df[['stock_id', 'date', 'open', 'close', 'high', 'low', 'volume']]

            async with AsyncSession(infra.db.async_engine) as session:
                await infra.db.batch_insert_or_update(session, USStockPrice, df)

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
