import datetime as dt

import pandas as pd

from finance_bot.strategy.base import StrategyBase
from finance_bot.ticker_db.ticker_db import Ticker, TickerDB


class FinlabStrategy(StrategyBase):
    name = 'Finlab 優等生策略'

    def select_tickers(self, date: dt.datetime) -> [Ticker]:
        df = self.ticker_db.get_all_metrics()
        df = df.sort_index()
        df = df.loc[date]
        df = df.set_index('symbol')

        c1 = df['market_capitalization'] < 10000000000
        c2 = df['free_cash_flow'] > 0
        c3 = df['return_on_equity'] > df['return_on_equity'].mean()
        c4 = df['operating_income_growth_rate'] > 0
        df = df[c1 & c2 & c3 & c4]
        return df.index.map(lambda symbol: self.ticker_db.get_ticker(symbol)).tolist()

    def is_buy_point(self, symbol: str, date: dt.datetime):
        tickers = self.select_tickers(date)
        if not tickers:
            return False

        df = self.ticker_db.get_all_metrics(tickers)
        df = df.loc[date]
        df = df.set_index('symbol')

        df = df.nlargest(5, 'operating_income_growth_rate')
        return symbol in df.index

    def is_sell_point(self, symbol: str, date: dt.datetime):
        tickers = self.select_tickers(date)
        return symbol not in [ticker.symbol for ticker in tickers]


if __name__ == '__main__':
    ticker_db = TickerDB()
    strategy = FinlabStrategy(ticker_db)
    strategy.select_tickers(dt.datetime(year=2020, month=1, day=1))
