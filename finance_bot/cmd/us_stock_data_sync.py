import asyncio
import click

from finance_bot.core import USStockDataSync


def create_us_stock_data_sync_cli():
    @click.group('us_stock_data_sync')
    def us_stock_data_sync():
        """資料同步"""
        pass

    ds = USStockDataSync()

    @us_stock_data_sync.command('start')
    def start_server():
        """啟動服務"""
        ds.start()

    @us_stock_data_sync.group('update')
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

    return us_stock_data_sync
