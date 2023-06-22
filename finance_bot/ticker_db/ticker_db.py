import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from finance_bot.ticker_db.database import get_engine
from finance_bot.ticker_db.updater import FinlabUpdater, FinmindUpdater


class Ticker:
    def __init__(self, ticker_db: 'TickerDB', symbol: str):
        self.ticker_db = ticker_db
        self.symbol = symbol

    def get_close_prices(self) -> pd.Series:
        df = pd.read_sql(
            sql=text("SELECT symbol, price, date FROM finlab_price_close WHERE symbol=:symbol"),
            params={'symbol': self.symbol},
            con=self.ticker_db.engine,
            index_col='date',
            parse_dates=['date'],
        )
        return df['price']


class TickerDB:

    def __init__(self):
        self.engine = get_engine()
        self.session = Session(self.engine)

        self.finlab_updater = FinlabUpdater(self.session)
        self.finmind_updater = FinmindUpdater(self.session)

        self._ticker_cache = {}

    def get_ticker(self, symbol: str) -> Ticker:
        if not self._ticker_cache.get(symbol):
            self._ticker_cache[symbol] = Ticker(self, symbol)
        return self._ticker_cache[symbol]


if __name__ == '__main__':
    ticker_db = TickerDB()
    ticker = ticker_db.get_ticker('0050')
    print(ticker.get_close_prices())
