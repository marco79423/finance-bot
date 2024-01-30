import asyncio

from finance_bot.core import TWStockDataSync
from finance_bot.core.tw_stock_data_sync import MarketData
from finance_bot.infrastructure import infra


def export_price_data_to_multicharts(data):
    for stock_id in data.stocks[data.stocks['tracked'] == 1].index:
        print(f'更新 {stock_id} ...')
        df = data[stock_id].prices[['open', 'high', 'low', 'close', 'volume']]
        if df.empty:
            continue

        target_path = infra.path.multicharts_folder / 'prices' / f'{stock_id}.csv'
        df.to_csv(target_path)
    print(f'更新股價結束')


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(TWStockDataSync().updater.rebuild_cache())

    market_data = MarketData()
    export_price_data_to_multicharts(market_data)


if __name__ == '__main__':
    main()
