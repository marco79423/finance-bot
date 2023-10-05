import abc
import dataclasses
from typing import Optional

import pandas as pd
import plotly.express as px

from finance_bot.core import TWStockManager
from finance_bot.core.tw_stock_manager.data_getter import DataGetter


class StrategyBase(abc.ABC):
    name: str
    params: dict = {}
    data: DataGetter
    buy_sig: pd.DataFrame
    sell_sig: pd.DataFrame
    sort_f: pd.DataFrame

    @abc.abstractmethod
    def handle(self):
        pass


class Strategy(StrategyBase):
    name = '基礎策略'
    params = dict(
        partition=10,
        stop_loss_rate=10,
    )

    def __init__(self):
        self.sma5 = self.data.close.rolling(window=5).mean()
        self.sma20 = self.data.close.rolling(window=20).mean()

    # noinspection PyTypeChecker
    def handle(self):
        self.buy_sig = (self.sma5 > self.sma20) & (self.sma5.shift(1) < self.sma20.shift(1)) & (self.data.close > 15)
        self.sell_sig = (self.sma5 < self.sma20) & (self.sma5.shift(1) > self.sma20.shift(1))


@dataclasses.dataclass
class Position:
    """投資部位"""
    stock_id: str
    shares: int
    start_date: pd.Timestamp
    end_date: pd.Timestamp

    start_price: float
    end_price: float

    max_price: Optional[float] = None
    min_price: Optional[float] = None

    @property
    def total_return(self):
        return (self.end_price - self.start_price) * self.shares

    @property
    def holding_period(self) -> pd.Timedelta:
        return self.end_date - self.start_date

    @property
    def return_rate(self) -> float:
        return (self.end_price - self.start_price) / self.start_price

    @property
    def max_return_rate(self) -> float:
        return (self.max_price - self.start_price) / self.start_price

    @property
    def min_return_rate(self) -> float:
        return (self.min_price - self.start_price) / self.start_price


@dataclasses.dataclass
class Result:
    strategy_name: str
    init_funds: int
    final_funds: int
    start: pd.Timestamp
    end: pd.Timestamp
    trades: pd.DataFrame
    equity_curve: pd.Series

    _analysis_trades: Optional[pd.DataFrame] = None

    @property
    def analysis_trades(self):
        if self._analysis_trades is None:
            df = self.trades.copy()
            df['total_return'] = (df['end_price'] - df['start_price']) * df['shares']
            self._analysis_trades = df
        return self._analysis_trades

    def show(self):
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None):
            print(self.analysis_trades)

        fig = px.line(
            data_frame=pd.DataFrame({
                '權益': self.equity_curve,
            }),
            title=self.strategy_name
        )
        fig.show()


class Backtester:
    """

    * 隔天買入漲停價
    * 隔天賣出跌停價
    """
    fee_discount = 0.6

    def __init__(self, data):
        self.data = data

    def run(self, stock_id, init_funds, strategy_class, start, end):
        start = pd.Timestamp(start)
        end = pd.Timestamp(end)

        stock_data = self.data[stock_id]

        all_close_prices = stock_data.close.ffill()
        all_open_prices = stock_data.open.ffill()

        strategy_class.data = stock_data
        strategy = strategy_class()
        strategy.handle()

        # 手續費和稅的比例
        fee_rate = 1.425 / 1000 * self.fee_discount  # 0.1425％
        tax_rate = 3 / 1000  # 政府固定收 0.3 %

        # 初始化資金和股票數量
        funds = init_funds
        trades = pd.DataFrame(
            columns=['status', 'stock_id', 'shares', 'start_date', 'start_price', 'end_date', 'end_price'])
        current_position = None

        buy_sig = strategy.buy_sig.loc[start:end]  # 篩選時間
        yesterday_buy_sig = buy_sig.shift(1).fillna(False)  # 隔天

        sell_sig = strategy.sell_sig.loc[start:end]  # 篩選時間
        yesterday_sell_sig = sell_sig.shift(1).fillna(False)  # 隔天

        all_date_range = all_close_prices.loc[start:end].index  # 交易日

        equity_curve = []
        for today in all_date_range:
            today_open_price = all_open_prices.at[today]
            today_close_price = all_close_prices.at[today]

            if current_position:
                current_position['end_price'] = today_close_price

                if yesterday_sell_sig.at[today]:
                    current_position['end_price'] = today_open_price
                    current_position['end_date'] = today
                    current_position['status'] = 'close'
                    funds += current_position['shares'] * current_position['end_price'] * (1 - fee_rate - tax_rate)
                    trades = pd.concat([trades, pd.DataFrame([current_position], columns=trades.columns)])
                    current_position = None

            else:
                if yesterday_buy_sig.at[today]:
                    shares = int((funds / (today_open_price * (1 + fee_rate)) // 1000) * 1000)
                    if shares < 1000:
                        continue

                    current_position = {
                        'status': 'open',
                        'stock_id': stock_id,
                        'shares': shares,
                        'start_date': today,
                        'start_price': today_open_price,
                        'end_price': today_open_price,
                    }

                    funds -= shares * (today_open_price * (1 + fee_rate))

            current_equity = funds
            if current_position:
                current_equity += current_position['end_price'] * current_position['shares']
            equity_curve.append(current_equity)

        if current_position:
            trades = pd.concat([trades, pd.DataFrame([current_position], columns=trades.columns)])
        trades = trades.reset_index(drop=True)

        equity_curve = pd.Series(equity_curve, index=all_date_range)
        return Result(
            strategy_name=strategy.name,
            start=start,
            end=end,
            init_funds=init_funds,
            final_funds=funds,
            trades=trades,
            equity_curve=equity_curve
        )


def main():
    backtester = Backtester(TWStockManager().data)

    result = backtester.run(
        stock_id='0050',
        init_funds=600000,
        strategy_class=Strategy,
        start='2015-08-01',
        end='2023-08-10',
    )
    result.show()


if __name__ == '__main__':
    main()
