from finance_bot.core import TWStockManager
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
    data = TWStockManager().data
    data.rebuild_cache()

    export_price_data_to_multicharts(data)


if __name__ == '__main__':
    main()