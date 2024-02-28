import pandas as pd
from sqlalchemy import text

from finance_bot.core.tw_stock_trade.strategy.base import StrategyBase, SignalBase, SignalStrategyBase, AndSignal, \
    SortSignalBase
from finance_bot.infrastructure import infra


class IndividualStockSignal(SignalBase):
    name = 'individual_stock'

    _stock_list = []

    def init(self, data):
        task_stock_tag_df = pd.read_sql(
            sql=text("SELECT * FROM tw_stock_tag"),
            con=infra.db.engine,
        )
        df = task_stock_tag_df[task_stock_tag_df['name'] == '個股']
        self._stock_list = df['stock_id'].to_list()

        return dict(
        )

    def handle(self, strategy: StrategyBase):
        cond1 = pd.Series([True] * len(self._stock_list), index=self._stock_list)

        return (
            cond1,
            '',
        )


class StockTagSignal(SignalBase):
    name = 'stock_tag'

    params = dict(
        st_tag='自選1',
    )

    _stock_list = []

    def init(self, data):
        task_stock_tag_df = pd.read_sql(
            sql=text("SELECT * FROM tw_stock_tag"),
            con=infra.db.engine,
        )
        df = task_stock_tag_df[task_stock_tag_df['name'] == self.params['st_tag']]
        self._stock_list = df['stock_id'].to_list()

        return dict(
        )

    def handle(self, strategy: StrategyBase):
        cond1 = pd.Series([True] * len(self._stock_list), index=self._stock_list)

        return (
            cond1,
            '',
        )


class EmptyHoldingStockSignal(SignalBase):
    name = 'empty_holding'

    def handle(self, strategy: StrategyBase):
        cond1 = (strategy.current_shares == 0).reindex(strategy.close.index, fill_value=True)

        return (
            cond1,
            '',
        )


class CloseOverSignal(SignalBase):
    name = 'close_over'

    params = dict(
        cos_close_over=10,
    )

    def handle(self, strategy: StrategyBase):
        cond1 = strategy.close > self.params['cos_close_over']

        return (
            cond1,
            '',
        )


class SMACrossOverSMASignal(SignalBase):
    name = 'sma_cross_over_sma'

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
    name = 'close_over_open'

    def handle(self, strategy: StrategyBase):
        cond1 = strategy.data.close.iloc[-1] > strategy.data.open.iloc[-1]

        return (
            cond1,
            '',
        )


class UnderVROCSignal(SignalBase):
    """量變動速率指標"""
    name = 'under_vroc'

    params = dict(
        uvroc_days=10,
        uvroc_under=1,
    )

    def init(self, data):
        uvroc_days = self.params['uvroc_days']
        return dict(
            uvroc_vroc=(data.volume - data.volume.shift(uvroc_days)) / data.volume.shift(uvroc_days),
        )

    def handle(self, strategy: StrategyBase):
        vroc = strategy.i('uvroc_vroc')
        cond1 = vroc.iloc[-1] < self.params['uvroc_under']

        return (
            cond1,
            '',
        )


class GoodProfitSellSignal(SignalBase):
    name = 'good_profit_sell'

    params = dict(
        gps_ideal_growth_rate=5,
        gps_accept_loss_rate=2
    )

    def handle(self, strategy: StrategyBase):
        cond1 = strategy.growth_rate * 100 >= self.params['gps_ideal_growth_rate']
        cond2 = strategy.growth_rate * 100 < (strategy.max_growth_rate * 100 - self.params['gps_accept_loss_rate'])

        return (
            cond1 & cond2,
            lambda stock_id: f'{strategy.growth_rate[stock_id] * 100:.2f}%'
        )


class HasProfitSellSignal(SignalBase):
    name = 'has_profit_sell'
    params = dict(
        hp_sma_short=5,
        hp_sma_long=35,
    )

    def init(self, data):
        return dict(
            hps_sma_short=data.close.rolling(window=self.params['hp_sma_short']).mean(),
            hps_sma_long=data.close.rolling(window=self.params['hp_sma_long']).mean(),
        )

    def handle(self, strategy: StrategyBase):
        sma_short = strategy.i('hps_sma_short')
        sma_long = strategy.i('hps_sma_long')

        cond1 = strategy.has_profit
        cond2 = (sma_short.iloc[-1] < sma_long.iloc[-1]) & (sma_short.iloc[-2] > sma_long.iloc[-2])

        return (
            cond1 & cond2,
            'SMA'
        )


class RunSellSignal(SignalBase):
    name = 'run_sell'

    def handle(self, strategy: StrategyBase):
        cond1 = strategy.has_profit
        cond2 = strategy.today - strategy.entry_date > pd.Timedelta(days=30 * 2)
        return (
            cond1 & cond2,
            'run'
        )


class BasicSortSignal(SortSignalBase):

    def handle(self, strategy: StrategyBase):
        return pd.Series([1] * len(strategy.data.all_stock_ids), index=strategy.data.all_stock_ids)


class StrategyT1V1(SignalStrategyBase):
    name = '策略 T1V1'

    buy_signals = [
        AndSignal(
            IndividualStockSignal(),
            StockTagSignal(),
            EmptyHoldingStockSignal(),
            CloseOverSignal(),
            SMACrossOverSMASignal(),
            CloseOverOpenSignal(),
            UnderVROCSignal(),
        )
    ]

    sell_signals = [
        GoodProfitSellSignal(),
        HasProfitSellSignal(),
        RunSellSignal(),
    ]

    sort_signal = BasicSortSignal()
