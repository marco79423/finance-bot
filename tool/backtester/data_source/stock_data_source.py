from tool.backtester.data_source.data_adapter import StockDataAdapter


class Stock:

    def __init__(self, data_source: 'StockDataSource', product_id):
        self._data_source = data_source
        self._product_id = product_id

    @property
    def open(self):
        return self._data_source.open[self._product_id]

    @property
    def close(self):
        return self._data_source.close[self._product_id]

    @property
    def high(self):
        return self._data_source.high[self._product_id]

    @property
    def low(self):
        return self._data_source.low[self._product_id]

    @property
    def volume(self):
        return self._data_source.volume[self._product_id]


class StockDataSource:
    is_limit = False

    data_adapter_class = StockDataAdapter

    def __init__(self, all_stock_ids=None, start=None, end=None):
        self._data_adapter = self.data_adapter_class(
            all_stock_ids=all_stock_ids,
            start=start,
            end=end,
        )
        self._current_time = self._data_adapter.start_time

    def __getitem__(self, stock_id) -> Stock:
        return Stock(self, stock_id)

    def set_time(self, time):
        self._current_time = time

    @property
    def start_time(self):
        return self._data_adapter.start_time

    @property
    def current_time(self):
        return self._current_time

    @property
    def end_time(self):
        return self._data_adapter.end_time

    @property
    def all_stock_ids(self):
        return self._data_adapter.close.loc[self.current_time].columns.tolist()

    @property
    def all_date_range(self):
        return self._data_adapter.close.loc[self.start_time:self.end_time].index  # 交易日

    def get_stock_high_price(self, stock_id):
        return self._data_adapter.high.loc[self.current_time, stock_id]

    def get_stock_low_price(self, stock_id):
        return self._data_adapter.low.loc[self.current_time, stock_id]

    def get_stock_close_price(self, stock_id):
        return self._data_adapter.close.loc[self.current_time, stock_id]

    @property
    def all_open(self):
        return self._data_adapter.open

    @property
    def all_close(self):
        return self._data_adapter.close

    @property
    def all_high(self):
        return self._data_adapter.high

    @property
    def all_low(self):
        return self._data_adapter.low

    @property
    def all_volume(self):
        return self._data_adapter.volume

    @property
    def open(self):
        end = self.current_time if self.is_limit else self.end_time
        return self.all_open[self.start_time:end]

    @property
    def close(self):
        end = self.current_time if self.is_limit else self.end_time
        return self.all_close[self.start_time:end]

    @property
    def high(self):
        end = self.current_time if self.is_limit else self.end_time
        return self.all_high[self.start_time:end]

    @property
    def low(self):
        end = self.current_time if self.is_limit else self.end_time
        return self.all_low[self.start_time:end]

    @property
    def volume(self):
        end = self.current_time if self.is_limit else self.end_time
        return self.all_volume[self.start_time:end]
