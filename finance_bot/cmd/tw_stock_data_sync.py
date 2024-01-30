import asyncio
import click

from finance_bot.core import TWStockDataSync


def create_tw_stock_data_sync_cli():
    @click.group('tw_stock_data_sync')
    def tw_stock_data_sync():
        """資料同步"""
        pass

    ds = TWStockDataSync()

    @tw_stock_data_sync.command('start')
    def start_server():
        """啟動服務"""
        ds.start()

    @tw_stock_data_sync.group('update')
    def update():
        """資料更新"""
        pass

    @update.command('cache')
    def update_cache():
        """更新快取"""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(ds.updater.rebuild_cache())

    @update.command('stocks')
    def update_stocks():
        loop = asyncio.get_event_loop()
        loop.run_until_complete(ds.updater.update_stocks())

    @update.command('prices')
    @click.option('-s', '--start', help='起始時間')
    @click.option('-e', '--end', help='結束時間')
    def update_prices(start, end):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(ds.updater.update_prices_for_date_range(start=start, end=end))

    @update.command('monthly-revenue')
    @click.option('-y', '--year', type=int, help='年')
    @click.option('-m', '--month', type=int, help='月')
    def update_prices(year, month):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(ds.updater.update_monthly_revenue(year=year, month=month))

    @update.command('financial-statements')
    @click.option('-sid', '--stock-id', type=str, help='股票 ID')
    @click.option('-y', '--year', type=int, help='年')
    @click.option('-q', '--quarter', type=int, help='年')
    @click.option('-f', '--force-update-db', is_flag=True, default=False, help='是否強迫更新 DB')
    def update_prices(stock_id, year, quarter, force_update_db):
        loop = asyncio.get_event_loop()

        if stock_id and year and quarter:
            loop.run_until_complete(ds.updater.update_financial_statements_for_stock_by_quarter(
                stock_id=stock_id,
                year=year,
                quarter=quarter,
            ))
        elif stock_id and not year and not quarter:
            loop.run_until_complete(ds.updater.update_all_financial_statements_for_stock_id(
                stock_id=stock_id,
                force_update_db=force_update_db,
            ))

        elif not stock_id and year and quarter:
            loop.run_until_complete(ds.updater.update_all_financial_statements_by_quarter(
                year=year,
                quarter=quarter,
            ))

        elif not stock_id and not year and not quarter:
            loop.run_until_complete(ds.updater.update_all_financial_statements(
                force_update_db=force_update_db,
            ))
        else:
            raise ValueError('不支援的操作')

    return tw_stock_data_sync
