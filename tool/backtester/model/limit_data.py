class LimitData:
    def __init__(self, data):
        self.data = data
        self.start_date = None
        self.end_date = None

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
