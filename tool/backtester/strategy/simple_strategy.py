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

        if sma5.iloc[-1] > sma20.iloc[-1] and sma5.iloc[-2] < sma20.iloc[-2] and self.data.close.iloc[-1] > 15:
            self.buy_next_day_market()
        elif sma5.iloc[-1] < sma20.iloc[-1] and sma5.iloc[-2] < sma20.iloc[-2]:
            self.sell_next_day_market()
