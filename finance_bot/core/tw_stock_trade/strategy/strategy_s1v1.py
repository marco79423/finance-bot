import abc
from types import FunctionType

import pandas as pd
from sqlalchemy import text

from finance_bot.core.tw_stock_trade.strategy.base import StrategyBase
from finance_bot.infrastructure import infra

task_stock_tag_df = pd.read_sql(
    sql=text("SELECT * FROM tw_stock_tag"),
    con=infra.db.engine,
)
df = task_stock_tag_df[task_stock_tag_df['name'] == '自選1']
available_stock_ids = df['stock_id'].to_list()


class SignalBase(abc.ABC):
    params = {}

    def init(self, data):
        return {}

    @abc.abstractmethod
    def handle(self, strategy: StrategyBase):
        pass


class AndSignal(SignalBase):

    def __init__(self, *signals, reason=''):
        self.signals = signals
        self.reason = reason

        self._params = {}
        for signal in self.signals:
            self._params.update(signal.params)
        for signal in self.signals:
            signal.params = self._params

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params):
        self._params = params
        for signal in self.signals:
            signal.params = self._params

    def init(self, data):
        result = {}
        for signal in self.signals:
            result.update(signal.init(data))
        return result

    def handle(self, strategy: StrategyBase):
        reasons = []
        conditions = []
        for signal in self.signals:
            cond, reason = signal.handle(strategy)
            conditions.append(cond)
            reasons.append(reason)

        df = pd.concat(conditions, axis=1)
        df = df.fillna(False)
        cond = df.all(axis=1)
        return (
            cond,
            self.reason if self.reason else '&'.join(reasons)
        )


class TargetStockSignal(SignalBase):
    available_stock_ids = available_stock_ids

    def handle(self, strategy: StrategyBase):
        cond1 = pd.Series([True] * len(self.available_stock_ids), index=self.available_stock_ids)

        return (
            cond1,
            '',
        )


class BuySignal(SignalBase):
    def init(self, data):
        return dict(
            sma10=data.close.rolling(window=10).mean(),
            sma35=data.close.rolling(window=35).mean(),
            voc10=(data.volume - data.volume.shift(10)) / data.volume.shift(10) * 100,
        )

    def handle(self, strategy: StrategyBase):
        sma10 = strategy.i('sma10')
        sma35 = strategy.i('sma35')
        voc10 = strategy.i('voc10')

        cond1 = (strategy.current_shares == 0).reindex(strategy.close.index, fill_value=True)
        cond2 = strategy.close > 10
        cond3 = (sma10.iloc[-1] > sma35.iloc[-1]) & (sma10.iloc[-2] < sma35.iloc[-2])
        cond4 = strategy.data.close.iloc[-1] > strategy.data.open.iloc[-1]
        cond5 = voc10.iloc[-1] < 100

        return (
            cond1 & cond2 & cond3 & cond4 & cond5,
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


class SignalStrategyBase(StrategyBase):
    buy_signals = []
    sell_signals = []

    def __init__(self):
        self._params = {}
        for signal in [*self.buy_signals, *self.sell_signals]:
            self._params.update(signal.params)
        for signal in [*self.buy_signals, *self.sell_signals]:
            signal.params = self._params

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params):
        self._params = params
        for signal in [*self.buy_signals, *self.sell_signals]:
            signal.params = self._params

    def init(self, data):
        result = {}
        for signal in [*self.buy_signals, *self.sell_signals]:
            result = {
                **result,
                **signal.init(data),
            }
        return result

    # noinspection PyTypeChecker
    def handle(self):
        for buy_signal in self.buy_signals:
            buy_cond, reason = buy_signal.handle(self)
            target_list = self.new_target_list([
                buy_cond
            ])

            for stock_id in target_list:
                if isinstance(reason, FunctionType):
                    reason = reason(stock_id)
                self.buy_next_day_market(stock_id, reason)

        for sell_signal in self.sell_signals:
            sell_cond, reason = sell_signal.handle(self)
            target_list = self.new_target_list([sell_cond])

            for stock_id in target_list:
                if isinstance(reason, FunctionType):
                    reason = reason(stock_id)
                self.sell_next_day_market(stock_id, note=reason)


class StrategyS1V1(SignalStrategyBase):
    name = '策略 S1V1'

    buy_signals = [
        AndSignal(
            TargetStockSignal(),
            BuySignal(),
        )
    ]

    sell_signals = [
        GoodProfitSellSignal(),
        HasProfitSellSignal(),
        RunSellSignal(),
    ]
