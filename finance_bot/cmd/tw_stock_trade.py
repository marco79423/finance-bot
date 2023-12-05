import click
import rich
from rich.table import Table

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

    @tw_stock_trade.group("broker")
    def broker():
        pass

    @broker.command('balance')
    def balance():
        rich.print('當前帳戶餘額', t.account_balance)

    @broker.command('positions')
    def positions():
        rich.print('當前持倉：')

        table = Table()
        table.add_column('股票 ID')
        table.add_column('股數')
        table.add_column('入場價')

        for position in t.positions:
            table.add_row(
                position['stock_id'],
                str(position['shares']),
                str(position['entry_price']) + '元',
            )
        rich.print(table)

    return tw_stock_trade
