import pandas as pd

from finance_bot.infrastructure import infra
from tool.backtester.strategy.base import StrategyBase

df = pd.read_csv(infra.path.multicharts_folder / f'stock_list_2.csv', header=None, index_col=0, dtype={0: str})


class StrategyS1V0(StrategyBase):
    name = '策略 S1V0'
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

        if self.current_shares == 0:
            buy_c = True
            buy_c = buy_c and self.close > 10
            buy_c = buy_c and sma10.iloc[-1] > sma35.iloc[-1] and sma10.iloc[-2] < sma35.iloc[-2]
            buy_c = buy_c and self.data.close.iloc[-1] > self.data.open.iloc[-1]
            buy_c = buy_c and voc10.iloc[-1] < 100

            if buy_c:
                self.buy_next_day_market()
        else:
            profit_rate = 5
            has_profit = self.has_profit
            has_good_profit = (self.close - self.entry_price) / self.entry_price * 100 >= profit_rate

            cross_under_sma = sma5.iloc[-1] < sma35.iloc[-1] and sma5.iloc[-2] > sma35.iloc[-2]
            too_long = self.today - self.entry_date > pd.Timedelta(days=40)

            if has_good_profit:
                self.sell_next_day_market(note=f'{profit_rate}%')
            elif cross_under_sma and has_profit:
                self.sell_next_day_market(note=f'SMA')
            elif too_long and has_profit:
                self.sell_next_day_market(note='run')
