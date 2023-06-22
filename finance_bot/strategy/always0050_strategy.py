import datetime as dt

import pandas as pd

from finance_bot.strategy.base import StrategyBase
from finance_bot.ticker_db.ticker_db import Ticker


class Always0050Strategy(StrategyBase):
    name = '永遠 0050 策略'

    def select_tickers(self, date: dt.datetime) -> [Ticker]:
        return [
            self.ticker_db.get_ticker(symbol='0050'),
        ]

    def get_buy_points(self, symbol: str):
        close_prices = self.ticker_db.get_ticker(symbol='0050').get_close_prices()
        return pd.Series(True, index=close_prices.index)

    def get_sell_points(self, symbol: str):
        close_prices = self.ticker_db.get_ticker(symbol='0050').get_close_prices()
        return pd.Series(False, index=close_prices.index)
