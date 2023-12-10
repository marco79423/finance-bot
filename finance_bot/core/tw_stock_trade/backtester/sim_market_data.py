from finance_bot.core.tw_stock_trade.market_data import MarketData


class SimMarketData(MarketData):
    is_limit = False

    def __init__(self, start, end):
        super().__init__()
        self._start_time = start
        self._end_time = end
        self._current_time = self._start_time

    def sync(self):
        pass

    def set_time(self, time):
        self._current_time = time

    @property
    def start_time(self):
        return self._start_time

    @property
    def current_time(self):
        return self._current_time

    @property
    def end_time(self):
        return self._end_time

    @property
    def all_date_range(self):
        return self._data_adapter.close.loc[self.start_time:self.end_time].index  # 交易日

    def get_stock_high_price(self, stock_id):
        return self._data_adapter.high.loc[self.current_time, stock_id]

    def get_stock_low_price(self, stock_id):
        return self._data_adapter.low.loc[self.current_time, stock_id]

    def get_stock_open_price(self, stock_id):
        return self._data_adapter.open.loc[self.current_time, stock_id]

    def get_stock_close_price(self, stock_id):
        return self._data_adapter.close.loc[self.current_time, stock_id]

    @property
    def open(self):
        end = self.current_time if self.is_limit else self.end_time
        return self._data_adapter.open[self.start_time:end]

    @property
    def close(self):
        end = self.current_time if self.is_limit else self.end_time
        return self._data_adapter.close[:end]

    @property
    def high(self):
        end = self.current_time if self.is_limit else self.end_time
        return self._data_adapter.high[:end]

    @property
    def low(self):
        end = self.current_time if self.is_limit else self.end_time
        return self._data_adapter.low[:end]

    @property
    def volume(self):
        end = self.current_time if self.is_limit else self.end_time
        return self._data_adapter.volume[:end]
