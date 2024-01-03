import click

from finance_bot.core.tw_stock_backtest import TWStockBacktest


def create_tw_stock_backtest_cli():
    @click.group('tw_stock_backtest')
    def tw_stock_backtest():
        """台股回測"""
        pass

    t = TWStockBacktest()

    @tw_stock_backtest.command("start")
    def start_server():
        """啟動服務"""
        t.start()

    return tw_stock_backtest
