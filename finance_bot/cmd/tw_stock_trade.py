import click

from finance_bot.core.tw_stock_trade import TWStockTrade


def create_tw_stock_trade_cli():
    @click.group('tw_stock_trade')
    def tw_stock_trade():
        """台股交易"""
        pass

    t = TWStockTrade()

    @tw_stock_trade.command("start")
    def start_server():
        """啟動服務"""
        t.start()

    return tw_stock_trade
