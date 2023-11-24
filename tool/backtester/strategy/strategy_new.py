import pandas as pd

from finance_bot.infrastructure import infra
from tool.backtester.strategy.base import StrategyBase

df = pd.read_csv(infra.path.multicharts_folder / f'stock_list_2.csv', header=None, index_col=0, dtype={0: str})


class StrategyNew(StrategyBase):
    name = '策略 New'
    params = dict(
    )
    available_stock_ids = df.index.to_list()

    def init(self, data):
        return dict(
            sma5=data.close.rolling(window=5).mean(),
            sma10=data.close.rolling(window=10).mean(),
            sma35=data.close.rolling(window=35).mean(),
            voc10=(data.volume - self.data.volume.shift(10)) / data.volume.shift(10) * 100,
        )

    # noinspection PyTypeChecker
    def handle(self):
        sma5 = self.i('sma5')
        sma10 = self.i('sma10')
        sma35 = self.i('sma35')
        voc10 = self.i('voc10')

        target_list = self.new_target_list([
            self.broker.current_shares == 0,
            self.close > 10,
            (sma10.iloc[-1] > sma35.iloc[-1]) & (sma10.iloc[-2] < sma35.iloc[-2]),
            self.data.close.iloc[-1] > self.data.open.iloc[-1],
            voc10.iloc[-1] < 100,
        ])

        for stock_id in target_list:
            self.buy_next_day_market(stock_id)

        # good profit
        ideal_growth_rate = 5
        accept_loss_rate = 5
        target_list = self.new_target_list([
            self.growth_rate * 100 >= ideal_growth_rate,
            self.growth_rate * 100 < (self.max_growth_rate * 100 - accept_loss_rate),
        ], available_list=self.broker.holding_stock_ids)
        for stock_id in target_list:
            self.sell_next_day_market(stock_id, note=f'{self.growth_rate[stock_id]}%')

        # has profit
        target_list = self.new_target_list([
            self.has_profit,
            (sma5.iloc[-1] < sma35.iloc[-1]) & (sma5.iloc[-2] > sma35.iloc[-2])
        ], available_list=self.broker.holding_stock_ids)
        for stock_id in target_list:
            self.sell_next_day_market(stock_id, note=f'SMA')

        # run
        target_list = self.new_target_list([
            self.has_profit,
            self.today - self.entry_date > pd.Timedelta(days=40),
        ], available_list=self.broker.holding_stock_ids)
        for stock_id in target_list:
            self.sell_next_day_market(stock_id, note=f'run')
