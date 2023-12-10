from .data_adapter import DataAdapter


class StockData:

    def __init__(self, market_data: 'MarketData', product_id):
        self._market_data = market_data
        self._product_id = product_id

    @property
    def open(self):
        return self._market_data.open[self._product_id]

    @property
    def close(self):
        return self._market_data.close[self._product_id]

    @property
    def high(self):
        return self._market_data.high[self._product_id]

    @property
    def low(self):
        return self._market_data.low[self._product_id]

    @property
    def volume(self):
        return self._market_data.volume[self._product_id]


class MarketData:
    data_adapter_class = DataAdapter

    def __init__(self):
        self._data_adapter = self.data_adapter_class()
        self._data_adapter.sync()

    def __getitem__(self, stock_id) -> StockData:
        return StockData(self, stock_id)

    def sync(self):
        self._data_adapter.sync()

    @property
    def start_time(self):
        return self._data_adapter.start_time

    @property
    def current_time(self):
        return self._data_adapter.end_time

    @property
    def all_stock_ids(self):
        return self._data_adapter.close.loc[self.current_time].columns.tolist()

    @property
    def all_date_range(self):
        return self._data_adapter.close.loc[self.start_time:self.current_time].index  # 交易日

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
        return self._data_adapter.open

    @property
    def close(self):
        return self._data_adapter.close

    @property
    def high(self):
        return self._data_adapter.high

    @property
    def low(self):
        return self._data_adapter.low

    @property
    def volume(self):
        return self._data_adapter.volume
