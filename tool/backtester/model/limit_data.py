from finance_bot.core.tw_stock_manager.base import MarketDataBase


class LimitMarketData(MarketDataBase):
    def __init__(self, data, start_date=None, end_date=None):
        self._data = data
        self.start_date = start_date
        self.end_date = end_date

        self._open = self._data.open.ffill()
        self._close = self._data.close.ffill()
        self._high = self._data.high.ffill()
        self._low = self._data.low.ffill()
        self._volume = self._data.volume.ffill()

    @property
    def raw(self):
        return self._data

    @property
    def open(self):
        return self._open[self.start_date:self.end_date]

    @property
    def close(self):
        return self._close[self.start_date:self.end_date]

    @property
    def high(self):
        return self._high[self.start_date:self.end_date]

    @property
    def low(self):
        return self._low[self.start_date:self.end_date]

    @property
    def volume(self):
        return self._volume[self.start_date:self.end_date]
