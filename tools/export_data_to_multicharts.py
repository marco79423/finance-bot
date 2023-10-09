from finance_bot.core import TWStockManager
from finance_bot.infrastructure import infra

data = TWStockManager().data
data.rebuild_cache()

for stock_id in data.stocks[data.stocks['tracked'] == 1].index:
    print(f'更新 {stock_id} ...')
    df = data[stock_id].prices[['open', 'high', 'low', 'close', 'volume']]
    if df.empty:
        continue

    target_path = infra.path.multicharts_folder / f'{stock_id}.csv'
    df.to_csv(target_path)
print(f'更新股價結束')
