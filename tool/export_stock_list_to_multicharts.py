import asyncio

import pandas as pd

from finance_bot.core import TWStockDataSync
from finance_bot.core.tw_stock_data_sync import MarketData
from finance_bot.infrastructure import infra


def export_stock_list_to_multicharts(data):
    c = True
    c = c & (data.stocks['tracked'] == 1)  # 有追蹤
    c = c & (data.stocks.index.str.match(r'^[1-9]\d{3}$'))  # 個股
    # c = c & (data.stocks['industry'] == '半導體業')

    df = pd.read_csv(infra.path.multicharts_folder / f'stock_list.csv', header=None, index_col=0, dtype={0:str})
    c = c & data.stocks.index.isin(df.index)

    # 股價六個月都大於 10 的
    last_date = data.close.index.max()
    six_months_ago = last_date - pd.DateOffset(months=6)
    s = (data.close[six_months_ago:last_date].dropna() > 10).all()
    c = c & data.stocks.index.isin(s[s].index)

    # 股價六個月都小於 100 的
    s = data.high[six_months_ago:last_date].max() < 100
    c = c & data.stocks.index.isin(s[s].index)

    # 股價大於 10 的
    s = (data.close.dropna() > 10).all()
    c = c & data.stocks.index.isin(s[s].index)

    # 股價都小於 100 的
    s = data.high.max() < 100
    c = c & data.stocks.index.isin(s[s].index)

    df = pd.DataFrame({
        'stock_id': data.stocks[c].index,
    })

    target_path = infra.path.multicharts_folder / f'stock_list_2.csv'
    df.to_csv(target_path, index=False, header=False)


def main():
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(TWStockDataSync().updater.rebuild_cache())

    market_data = MarketData()
    export_stock_list_to_multicharts(market_data)


if __name__ == '__main__':
    main()
