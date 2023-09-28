from finance_bot.core import TWStockManager
from finance_bot.infrastructure import infra

data = TWStockManager().data
for stock_id in data.stocks.index:
    print(f'更新 {stock_id} ...')
    target_path = infra.path.multicharts_folder / f'{stock_id}.csv'

    prices_df = data[stock_id].prices
    df = prices_df[['open', 'high', 'low', 'close', 'volume']]
    df.to_csv(target_path)
print(f'更新股價結束')
