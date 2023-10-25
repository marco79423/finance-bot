from finance_bot.core.tw_stock_manager.base import MarketDataBase


class LimitMarketData(MarketDataBase):
    def __init__(self, data, start_date=None, end_date=None):
        self.data = data
        self.start_date = start_date
        self.end_date = end_date

    @property
    def open(self):
        return self.data.open[self.start_date:self.end_date]

    @property
    def close(self):
        return self.data.close[self.start_date:self.end_date]

    @property
    def high(self):
        return self.data.high[self.start_date:self.end_date]

    @property
    def low(self):
        return self.data.low[self.start_date:self.end_date]

    @property
    def volume(self):
        return self.data.volume[self.start_date:self.end_date]
