import pandas as pd
from sqlalchemy import text

from finance_bot.core.tw_stock_trade.strategy.base import StrategyBase, SignalBase, SignalStrategyBase, AndSignal
from finance_bot.infrastructure import infra

task_stock_tag_df = pd.read_sql(
    sql=text("SELECT * FROM tw_stock_tag"),
    con=infra.db.engine,
)
df = task_stock_tag_df[task_stock_tag_df['name'] == '自選1']
available_stock_ids = df['stock_id'].to_list()


class TargetStockSignal(SignalBase):
    available_stock_ids = available_stock_ids

    def handle(self, strategy: StrategyBase):
        cond1 = pd.Series([True] * len(self.available_stock_ids), index=self.available_stock_ids)

        return (
            cond1,
            '',
        )


class EmptyHoldingStockSignal(SignalBase):

    def handle(self, strategy: StrategyBase):
        cond1 = (strategy.current_shares == 0).reindex(strategy.close.index, fill_value=True)

        return (
            cond1,
            '',
        )


class CloseOverSignal(SignalBase):
    params = dict(
        cos_close_over=10,
    )

    def handle(self, strategy: StrategyBase):
        cond1 = strategy.close > self.params['cos_close_over']

        return (
            cond1,
            '',
        )


class SMACrossOverSMA(SignalBase):
    params = dict(
        scos_sma_short=10,
        scos_sma_long=35,
    )

    def init(self, data):
        return dict(
            scos_sma_short=data.close.rolling(window=self.params['scos_sma_short']).mean(),
            scos_sma_long=data.close.rolling(window=self.params['scos_sma_long']).mean(),
        )

    def handle(self, strategy: StrategyBase):
        sma_short = strategy.i('scos_sma_short')
        sma_long = strategy.i('scos_sma_long')

        cond1 = (sma_short.iloc[-1] > sma_long.iloc[-1]) & (sma_short.iloc[-2] < sma_long.iloc[-2])

        return (
            cond1,
            '',
        )


class CloseOverOpenSignal(SignalBase):

    def handle(self, strategy: StrategyBase):
        cond1 = strategy.data.close.iloc[-1] > strategy.data.open.iloc[-1]

        return (
            cond1,
            '',
        )


class BuySignal(SignalBase):
    def init(self, data):
        return dict(
            voc10=(data.volume - data.volume.shift(10)) / data.volume.shift(10) * 100,
        )

    def handle(self, strategy: StrategyBase):
        voc10 = strategy.i('voc10')
        cond1 = voc10.iloc[-1] < 100

        return (
            cond1,
            '',
        )


class GoodProfitSellSignal(SignalBase):
    params = dict(
        ideal_growth_rate=5,
        accept_loss_rate=2
    )

    def handle(self, strategy: StrategyBase):
        cond1 = strategy.growth_rate * 100 >= self.params.get('ideal_growth_rate', 5)
        cond2 = strategy.growth_rate * 100 < (strategy.max_growth_rate * 100 - self.params.get('accept_loss_rate', 2))

        return (
            cond1 & cond2,
            lambda stock_id: f'{strategy.growth_rate[stock_id] * 100:.2f}%'
        )


class HasProfitSellSignal(SignalBase):
    def init(self, data):
        return dict(
            sma5=data.close.rolling(window=5).mean(),
            sma35=data.close.rolling(window=35).mean(),
        )

    def handle(self, strategy: StrategyBase):
        sma5 = strategy.i('sma5')
        sma35 = strategy.i('sma35')

        cond1 = strategy.has_profit
        cond2 = (sma5.iloc[-1] < sma35.iloc[-1]) & (sma5.iloc[-2] > sma35.iloc[-2])

        return (
            cond1 & cond2,
            'SMA'
        )


class RunSellSignal(SignalBase):
    def handle(self, strategy: StrategyBase):
        cond1 = strategy.has_profit
        cond2 = strategy.today - strategy.entry_date > pd.Timedelta(days=30 * 2)
        return (
            cond1 & cond2,
            'run'
        )


class StrategyS1V1(SignalStrategyBase):
    name = '策略 S1V1'

    buy_signals = [
        AndSignal(
            TargetStockSignal(),
            EmptyHoldingStockSignal(),
            CloseOverSignal(),
            SMACrossOverSMA(),
            CloseOverOpenSignal(),
            BuySignal(),
        )
    ]

    sell_signals = [
        GoodProfitSellSignal(),
        HasProfitSellSignal(),
        RunSellSignal(),
    ]
