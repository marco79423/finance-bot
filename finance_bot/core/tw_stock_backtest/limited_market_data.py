from finance_bot.core.tw_stock_data_sync.market_data import MarketDataBase


class LimitedMarketData(MarketDataBase):
    is_limit = False

    def __init__(self, market_data, start, end):
        self._market_data = market_data
        self._start_time = start
        self._end_time = end
        self._current_time = self._start_time

    def sync(self):
        pass

    def set_current_time(self, time):
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
    def all_stock_ids(self):
        return self._market_data.all_stock_ids

    @property
    def all_date_range(self):
        return self._market_data.close.loc[self.start_time:self.end_time].index  # 交易日

    def get_stock_high_price(self, stock_id):
        return self._market_data.high.loc[self.current_time, stock_id]

    def get_stock_low_price(self, stock_id):
        return self._market_data.low.loc[self.current_time, stock_id]

    def get_stock_open_price(self, stock_id):
        return self._market_data.open.loc[self.current_time, stock_id]

    def get_stock_close_price(self, stock_id):
        return self._market_data.close.loc[self.current_time, stock_id]

    @property
    def prices(self):
        end = self.current_time if self.is_limit else self.end_time
        return self._market_data.prices.loc[self.start_time:end]

    @property
    def open(self):
        end = self.current_time if self.is_limit else self.end_time
        return self._market_data.open[self.start_time:end]

    @property
    def close(self):
        end = self.current_time if self.is_limit else self.end_time
        return self._market_data.close[self.start_time:end]

    @property
    def high(self):
        end = self.current_time if self.is_limit else self.end_time
        return self._market_data.high[self.start_time:end]

    @property
    def low(self):
        end = self.current_time if self.is_limit else self.end_time
        return self._market_data.low[self.start_time:end]

    @property
    def volume(self):
        end = self.current_time if self.is_limit else self.end_time
        return self._market_data.volume[self.start_time:end]

    @property
    def monthly_revenue(self):
        end = self.current_time if self.is_limit else self.end_time
        return self._market_data.monthly_revenue[self.start_time:end]

    @property
    def traded_value(self):
        end = self.current_time if self.is_limit else self.end_time
        return self._market_data.traded_value[self.start_time:end]

    @property
    def transaction_count(self):
        end = self.current_time if self.is_limit else self.end_time
        return self._market_data.transaction_count[self.start_time:end]

    @property
    def last_bid_price(self):
        end = self.current_time if self.is_limit else self.end_time
        return self._market_data.last_bid_price[self.start_time:end]

    @property
    def last_bid_volume(self):
        end = self.current_time if self.is_limit else self.end_time
        return self._market_data.last_bid_volume[self.start_time:end]

    @property
    def last_ask_price(self):
        end = self.current_time if self.is_limit else self.end_time
        return self._market_data.last_ask_price[self.start_time:end]

    @property
    def last_ask_volume(self):
        end = self.current_time if self.is_limit else self.end_time
        return self._market_data.last_ask_volume[self.start_time:end]

    @property
    def share_capital(self):
        end = self.current_time if self.is_limit else self.end_time
        return self._market_data.share_capital[self.start_time:end]

    @property
    def total_shares_outstanding(self):
        end = self.current_time if self.is_limit else self.end_time
        return self._market_data.total_shares_outstanding[self.start_time:end]

    @property
    def market_capitalization(self):
        end = self.current_time if self.is_limit else self.end_time
        return self._market_data.market_capitalization[self.start_time:end]
