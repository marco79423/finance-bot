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
        self.sort_f = self.data.close


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

    def show(self):
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None):
            df = self.trades.copy()
            df['total_return'] = (df['end_price'] - df['start_price']) * df['shares'] * 1000
            print(df)

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

    @property
    def filled_close(self):
        """補完空值的收盤價"""
        return self.data.close.ffill()

    @property
    def filled_open(self):
        """補完空值的開盤價"""
        return self.data.open.ffill()

    def run(self, init_funds, partition, stop_loss_rate, strategy_class, start, end):
        start = pd.Timestamp(start)
        end = pd.Timestamp(end)

        all_close_prices = self.filled_close
        all_open_prices = self.filled_open

        strategy_class.data = self.data
        strategy = strategy_class()
        strategy.handle()

        # 手續費和稅的比例
        fee_rate = 1.425 / 1000 * self.fee_discount  # 0.1425％
        tax_rate = 3 / 1000  # 政府固定收 0.3 %

        # 初始化資金和股票數量
        funds = init_funds
        trades = pd.DataFrame(columns=['status', 'stock_id', 'shares', 'start_date', 'start_price', 'end_date', 'end_price'])

        buy_sig = strategy.buy_sig.loc[start:end]  # 篩選時間
        buy_sig = buy_sig.loc[:, buy_sig.any()]  # 直接濾掉全部值為 False 的股票
        sort_f = strategy.sort_f.loc[buy_sig.index, buy_sig.columns]
        yesterday_buy_weight_sig = (buy_sig * sort_f).shift(1).fillna(0)  # 隔天

        sell_sig = strategy.sell_sig.loc[start:end]  # 篩選時間
        sell_sig = sell_sig.loc[:, sell_sig.any()]  # 直接濾掉全部值為 False 的股票
        yesterday_sell_sig = sell_sig.shift(1).fillna(False)  # 隔天

        all_date_range = all_close_prices.loc[start:end].index  # 交易日

        equity_curve = []
        for today in all_date_range:
            today_open_prices = all_open_prices.loc[today]
            today_close_prices = all_close_prices.loc[today]

            trades['end_price'].update(trades.loc[trades['status'] == 'open', 'stock_id'].map(today_close_prices))

            single_entry_limit = 0
            open_positions = trades[trades['status'] == 'open']
            if partition - len(open_positions) >= 1:
                single_entry_limit = funds // (partition - len(open_positions))

            holding_stock_ids = open_positions['stock_id']

            sell_stock_ids = []
            if today in yesterday_sell_sig.index:
                s = yesterday_sell_sig.loc[today]
                sell_stock_ids = s[s].index.tolist()

            open_cond = trades['status'] == 'open'
            sell_ids_cond = trades['stock_id'].isin(sell_stock_ids)
            new_close_positions = trades.loc[open_cond & sell_ids_cond]
            funds += sum(new_close_positions['shares'] * new_close_positions['end_price'] * (1 - fee_rate - tax_rate))

            trades.loc[open_cond & sell_ids_cond, 'end_date'] = today
            trades.loc[open_cond & sell_ids_cond, 'status'] = 'close'

            available_stock_ids = []
            if today in yesterday_buy_weight_sig.index:
                weight_s = yesterday_buy_weight_sig.loc[today]
                s = weight_s.sort_values(ascending=False)
                i = s.index[~s.index.isin(holding_stock_ids)]
                available_stock_ids = i[:partition].tolist()

            new_positions = []
            for stock_id in available_stock_ids:
                open_price = today_open_prices[stock_id]

                shares = int((single_entry_limit / (open_price * (1 + fee_rate)) // 1000) * 1000)
                if shares < 1000:
                    continue

                new_positions.append({
                    'status': 'open',
                    'stock_id': stock_id,
                    'shares': shares,
                    'start_date': today,
                    'start_price': open_price,
                    'end_price': today_close_prices[stock_id],
                })
                funds -= shares * (open_price * (1 + fee_rate))
            new_positions = pd.DataFrame(new_positions)

            trades = pd.concat([trades, new_positions])
            trades = trades.reset_index(drop=True)

            open_positions = trades.loc[trades['status'] == 'open']
            current_equity = funds + sum(open_positions['end_price'] * open_positions['shares'])
            equity_curve.append(current_equity)

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
        init_funds=600000,
        partition=5,
        stop_loss_rate=20,
        strategy_class=Strategy,
        start='2023-08-01',
        end='2023-08-10',
    )
    result.show()


if __name__ == '__main__':
    main()
