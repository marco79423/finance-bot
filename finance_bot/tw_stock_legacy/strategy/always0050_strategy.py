import datetime as dt

from finance_bot.tw_stock_legacy.strategy.base import StrategyBase
from finance_bot.tw_stock_legacy.ticker_db.ticker_db import Ticker


class Always0050Strategy(StrategyBase):
    name = '永遠 0050 策略'

    def select_tickers(self, date: dt.datetime) -> [Ticker]:
        return [
            self.ticker_db.get_ticker(symbol='0050'),
        ]

    def is_buy_point(self, symbol: str, date: dt.datetime) -> bool:
        return True

    def is_sell_point(self, symbol: str, date: dt.datetime) -> bool:
        return False
