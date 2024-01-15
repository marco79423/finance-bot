import asyncio
import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from finance_bot.core import DataSync
from finance_bot.infrastructure import infra
from finance_bot.model import TWStockTag


async def export_stock_list_to_tw_stock_tag(data):
    c = True
    c = c & (data.stocks['tracked'] == 1)  # 有追蹤
    c = c & (data.stocks.index.str.match(r'^[1-9]\d{3}$'))  # 個股

    df = pd.read_csv(infra.path.multicharts_folder / f'stock_list_2.csv', header=None, index_col=0, dtype={0: str})
    c = c & data.stocks.index.isin(df.index)

    df = pd.DataFrame({
        'stock_id': data.stocks[c].index,
        'name': '自選1',
        'reason': '手動自選'
    })

    async with AsyncSession(infra.db.async_engine) as session:
        await infra.db.batch_insert_or_update(session, TWStockTag, df)


async def export_stock_list_to_tw_stock_tag2(data):
    df = pd.read_sql(
        sql=text("SELECT DISTINCT stock_id FROM tw_stock_financial_statements"),
        con=infra.db.engine,
    )

    df = pd.DataFrame({
        'stock_id': df['stock_id'],
        'name': '個股',
        'reason': '透過月財報判斷個股'
    })

    async with AsyncSession(infra.db.async_engine) as session:
        await infra.db.batch_insert_or_update(session, TWStockTag, df)


async def main():
    data = DataSync().data

    # await export_stock_list_to_tw_stock_tag(data)
    await export_stock_list_to_tw_stock_tag2(data)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
