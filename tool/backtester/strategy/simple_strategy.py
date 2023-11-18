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

        target_list = self.new_target_list([
            sma5.iloc[-1] > sma20.iloc[-1],
            sma5.iloc[-2] < sma20.iloc[-2],
            self.close > 15
        ])
        for stock_id in target_list:
            self.buy_next_day_market(stock_id)

        target_list = self.new_target_list([
            sma5.iloc[-1] < sma20.iloc[-1],
            sma5.iloc[-2] < sma20.iloc[-2],
            self.close > 15,
        ], available_list=self.broker.holding_stock_ids)
        for stock_id in target_list:
            self.sell_next_day_market(stock_id)
