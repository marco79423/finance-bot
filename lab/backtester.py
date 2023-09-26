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
    close_date: pd.Timestamp

    start_price: float
    close_price: float

    max_price: Optional[float] = None
    min_price: Optional[float] = None

    @property
    def total_return(self):
        return (self.close_price - self.start_price) * self.shares

    @property
    def holding_period(self) -> pd.Timedelta:
        return self.close_date - self.start_date

    @property
    def return_rate(self) -> float:
        return (self.close_price - self.start_price) / self.start_price

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
    positions: pd.DataFrame
    close_positions: pd.DataFrame
    equity_curve: pd.Series

    @property
    def trades(self):
        return []

    # @property
    # def equity_curve(self):
    #     """權益曲線（Equity Curve）"""
    #     return pd.Series(np.random.randint(-1000, 1000, 100),
    #                      index=pd.date_range(start='2023-01-01', periods=100)).cumsum() + self.init_funds

    def show(self):
        fig = px.line(
            data_frame=pd.DataFrame({
                '權益': self.equity_curve,
            }),
            title=self.strategy_name
        )
        fig.show()
        print('已關倉')
        df = self.close_positions.copy()
        df['total_return'] = (df['close_price'] - df['start_price']) * df['shares'] * 1000
        print(df)

        print('仍持倉')
        df = self.positions.copy()
        df['total_return'] = (df['current_price'] - df['start_price']) * df['shares'] * 1000
        print(df)


class Backtester:
    """

    * 隔天買入漲停價
    * 隔天賣出跌停價
    """
    fee_discount = 0.6

    def __init__(self, data):
        self.data = data

    def run(self, init_funds, partition, stop_loss_rate, strategy_class, start, end):
        start = pd.Timestamp(start)
        end = pd.Timestamp(end)

        close_df = self.data.close.ffill()
        open_df = self.data.open.ffill()
        current_df = close_df

        strategy_class.data = self.data
        strategy = strategy_class()
        strategy.handle()

        # 手續費和稅的比例
        fee_rate = 1.425 / 1000 * self.fee_discount  # 0.1425％
        tax_rate = 3 / 1000  # 政府固定收 0.3 %

        # 初始化資金和股票數量
        funds = init_funds
        close_positions = pd.DataFrame(columns=['stock_id', 'shares', 'start_date', 'start_price', 'close_date', 'close_price', 'current_price'])
        positions = pd.DataFrame(columns=['stock_id', 'shares', 'start_date', 'start_price', 'close_date', 'close_price', 'current_price'])

        buy_s = strategy.buy_sig.loc[start:end]  # 篩選時間
        buy_s = buy_s.loc[:, buy_s.any()]  # 直接濾掉全部值為 False 的股票
        sort_f = strategy.sort_f.loc[buy_s.index, buy_s.columns]
        buy_weight_df = (buy_s * sort_f).shift(1).fillna(0) # 隔天

        sell_sig = strategy.sell_sig.loc[start:end]  # 篩選時間
        sell_sig = sell_sig.loc[:, sell_sig.any()]  # 直接濾掉全部值為 False 的股票
        sell_df = sell_sig.shift(1).fillna(False)  # 隔天

        date_range_i = close_df.loc[start:end].index # 交易日

        equity_curve = []
        for date in date_range_i:
            max_f = funds // (partition - len(positions)) if partition - len(positions) >= 1 else 0
            holding_stock_ids = positions['stock_id']

            open_s = open_df.loc[date]
            current_s = current_df.loc[date]

            sell_stock_ids = []
            if date in sell_df.index:
                s = sell_df.loc[date]
                sell_stock_ids = s[s].index.tolist()

            new_close_positions = positions[positions['stock_id'].isin(sell_stock_ids)].copy()
            if not new_close_positions.empty:
                new_close_positions['close_date'] = date
                new_close_positions['close_price'] = new_close_positions['stock_id'].map(open_s[new_close_positions['stock_id']])
                funds += sum(new_close_positions['shares'] * new_close_positions['close_price'] * (1 - fee_rate - tax_rate))
                close_positions = pd.concat([close_positions, new_close_positions])

            new_positions1 = positions[~positions['stock_id'].isin(sell_stock_ids)].copy()
            new_positions1['current_price'] = new_positions1['stock_id'].map(current_s[new_positions1['stock_id']])

            available_stock_ids = []
            if date in buy_weight_df.index:
                weight_s = buy_weight_df.loc[date]
                s = weight_s.sort_values(ascending=False)
                i = s.index[~s.index.isin(holding_stock_ids)]
                available_stock_ids = i[:partition].tolist()

            new_positions2 = []
            for stock_id in available_stock_ids:
                open_price = open_s[stock_id]
                current_price = current_s[stock_id]

                shares = (max_f / (open_price * (1 + fee_rate)) // 1000) * 1000
                if shares < 1000:
                    continue

                new_positions2.append({
                    'stock_id': stock_id,
                    'shares': shares,
                    'start_date': date,
                    'start_price': open_price,
                    'current_price': current_price,
                })
                funds -= shares * (open_price * (1 + fee_rate))
            new_positions2 = pd.DataFrame(new_positions2)

            positions = pd.concat([new_positions1, new_positions2])
            positions = positions.reset_index(drop=True)

            current_equity = funds + sum(positions['current_price'] * positions['shares'])
            equity_curve.append(current_equity)

        equity_curve = pd.Series(equity_curve, index=date_range_i)

        return Result(
            strategy_name=strategy.name,
            start=start,
            end=end,
            init_funds=init_funds,
            final_funds=funds,
            positions=positions,
            close_positions=close_positions,
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
