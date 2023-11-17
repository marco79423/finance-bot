from tool.backtester.strategy.base import StrategyBase


class SimpleStrategy(StrategyBase):
    name = '基礎策略'
    params = dict(
    )
    available_stock_ids = ['0050']

    # noinspection PyTypeChecker
    def handle(self):
        sma5 = self.data.close.rolling(window=5).mean()
        sma20 = self.data.close.rolling(window=20).mean()

        buy_cond = (sma5.iloc[-1] > sma20.iloc[-1])
        buy_cond = buy_cond & (sma5.iloc[-2] < sma20.iloc[-2])
        buy_cond = buy_cond & (self.close > 15)

        for stock_id in self.close[buy_cond].index:
            if stock_id in self.available_stock_ids:
                self.buy_next_day_market(stock_id)

        sell_cond = (sma5.iloc[-1] < sma20.iloc[-1])
        sell_cond = sell_cond & (sma5.iloc[-2] < sma20.iloc[-2])

        for stock_id in self.close[sell_cond].index:
            self.sell_next_day_market(stock_id)
