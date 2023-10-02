from finance_bot.core import TWStockManager
from finance_bot.infrastructure import infra

data = TWStockManager().data

for stock_id, stock in data.stocks[data.stocks['tracked'] == 1].iterrows():
    print(f'更新 {stock_id} ...')
    df = data[stock_id].prices[['open', 'high', 'low', 'close', 'volume']].copy()
    if df.empty:
        continue

    df['description'] = f'{stock.name} (Custom)'
    df['type'] = 'Stock'
    df['exchange'] = 'TWSE'  # TSEC

    target_path = infra.path.multicharts_folder / f'{stock_id}.csv'
    df.to_csv(target_path)
print(f'更新股價結束')
