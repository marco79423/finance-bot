import datetime as dt

from finance_bot.tw_stock.strategy.base import StrategyBase
from finance_bot.tw_stock.ticker_db.ticker_db import Ticker, TickerDB


class FinlabStrategy(StrategyBase):
    name = 'Finlab 優等生策略'

    def select_tickers(self, date: dt.datetime) -> [Ticker]:
        tickers = self.ticker_db.get_tickers(ticker_type='twse', date=date)
        if not tickers:
            return []
        df = self.ticker_db.get_ticker_metrics(tickers, date)
        df = df.set_index('symbol')

        c1 = df['market_capitalization'] < 10000000000
        c2 = df['free_cash_flow'] > 0
        c3 = df['return_on_equity'] > df['return_on_equity'].mean()
        c4 = df['operating_income_growth_rate'] > 0
        df = df[c1 & c2 & c3 & c4]
        df = df.nlargest(1, 'operating_income_growth_rate')
        return df.index.map(lambda symbol: self.ticker_db.get_ticker(symbol)).tolist()

    def is_buy_point(self, symbol: str, date: dt.datetime):
        ticker = self.ticker_db.get_ticker(symbol)
        close_prices = ticker.get_close_prices()
        buy_point = close_prices == close_prices.rolling(window=5).min()
        return date in buy_point.index

    def is_sell_point(self, symbol: str, date: dt.datetime):
        tickers = self.select_tickers(date)
        return tickers and tickers[0].symbol != symbol


if __name__ == '__main__':
    ticker_db = TickerDB()
    strategy = FinlabStrategy(ticker_db)
    tickers = strategy.select_tickers(dt.datetime(year=2020, month=12, day=1))
    print(tickers)
