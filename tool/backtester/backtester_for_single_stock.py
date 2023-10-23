import abc
import dataclasses
import math
from typing import Optional, List

import pandas as pd
import plotly.graph_objects as go

from finance_bot.core import TWStockManager


class LimitData:
    def __init__(self, data):
        self.data = data
        self.start_date = None
        self.end_date = None

    @property
    def open(self):
        return self.data.open[self.start_date:self.end_date]

    @property
    def close(self):
        return self.data.close[self.start_date:self.end_date]

    @property
    def high(self):
        return self.data.high[self.start_date:self.end_date]

    @property
    def low(self):
        return self.data.low[self.start_date:self.end_date]


class StrategyBase(abc.ABC):
    name: str
    params: dict = {}
    data: LimitData
    available_stock_ids: Optional[List[str]] = None

    _buy_next_day_open = False
    _sell_next_day_open = False

    @abc.abstractmethod
    def handle(self):
        pass

    def buy_next_day_open(self, confident_score=1):
        self._buy_next_day_open = True

    def sell_next_day_open(self):
        self._sell_next_day_open = True

    def inter_clean(self):
        self._buy_next_day_open = False
        self._sell_next_day_open = False


class MovingIndicator:
    def __init__(self, data, period):
        self.data = data
        self.period = period


class Strategy(StrategyBase):
    name = '基礎策略'
    params = dict(
    )
    available_stock_ids = ['0050']

    # noinspection PyTypeChecker
    def handle(self):
        sma5 = self.data.close.rolling(window=5).mean()
        sma20 = self.data.close.rolling(window=20).mean()

        if sma5.iloc[-1] > sma20.iloc[-1] and sma5.iloc[-2] < sma20.iloc[-2] and self.data.close.iloc[-1] > 15:
            self.buy_next_day_open()
        elif sma5.iloc[-1] < sma20.iloc[-1] and sma5.iloc[-2] < sma20.iloc[-2]:
            self.sell_next_day_open()


@dataclasses.dataclass
class Result:
    strategy_name: str
    init_funds: int
    final_funds: int
    start: pd.Timestamp
    end: pd.Timestamp
    trades: pd.DataFrame
    equity_curve: pd.Series
    data: LimitData

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

        data = [
            go.Candlestick(
                x=self.data.close.index,
                open=self.data.open,
                high=self.data.high,
                low=self.data.low,
                close=self.data.close,
                increasing_line_color='red',
                decreasing_line_color='green',
                name='K 線',
            )
        ]

        for idx, trade in self.analysis_trades.iterrows():
            data.append(
                go.Scatter(
                    x=[trade['start_date'], trade['end_date']],
                    y=[trade['start_price'], trade['end_price']],
                    line_color='red' if trade['total_return'] > 0 else 'green',
                    name=f'trade {idx}'
                )
            )

        data.append(
            go.Scatter(
                x=self.equity_curve.index,
                y=self.equity_curve,
                name='權益',
                xaxis="x",
                yaxis="y2"
            )
        )

        fig = go.Figure(
            data=data,
            layout=go.Layout(
                xaxis=dict(
                    title='日期',
                    rangeslider_visible=False,
                ),
                yaxis=dict(
                    title='股價',
                    domain=[0.5, 1],
                ),
                yaxis2=dict(
                    title='權益',
                    domain=[0, 0.5],
                ),
            )
        )

        for _, trade in self.trades.iterrows():
            fig.add_annotation(
                x=trade['start_date'],
                y=trade['start_price'],
                text="Buy",
                arrowhead=2,
                ax=0,
                ay=-30
            )
            fig.add_annotation(
                x=trade['end_date'],
                y=trade['end_price'],
                text="Sell",
                arrowhead=2,
                ax=0,
                ay=-30
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

        all_close_prices = stock_data.close.ffill()  # 補完空值的收盤價
        all_open_prices = stock_data.open.ffill()  # 補完空值的開盤價

        strategy_class.stock_id = stock_id
        strategy_class.data = LimitData(stock_data)
        strategy_class.data.start_date = start
        strategy = strategy_class()

        # 手續費和稅的比例
        fee_rate = 1.425 / 1000 * self.fee_discount  # 0.1425％
        tax_rate = 3 / 1000  # 政府固定收 0.3 %

        # 初始化資金和股票數量
        funds = init_funds
        trades = pd.DataFrame(
            columns=['status', 'stock_id', 'shares', 'start_date', 'start_price', 'end_date', 'end_price'])
        current_position = None

        all_date_range = all_close_prices.loc[start:end].index  # 交易日

        equity_curve = []
        for today in all_date_range:
            today_open_price = all_open_prices.at[today]
            today_close_price = all_close_prices.at[today]

            if current_position:
                current_position['end_price'] = today_close_price
                current_position['end_date'] = today

                if strategy._sell_next_day_open:
                    current_position['end_price'] = today_open_price
                    current_position['end_date'] = today
                    current_position['status'] = 'close'
                    funds += math.floor(current_position['shares'] * current_position['end_price'] * (1 - fee_rate - tax_rate))
                    trades = pd.concat([trades, pd.DataFrame([current_position], columns=trades.columns)])
                    current_position = None

            else:
                if strategy._buy_next_day_open:
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
                        'end_date': today,
                    }

                    funds -= math.ceil(shares * (today_open_price * (1 + fee_rate)))

            current_equity = funds
            if current_position:
                current_equity += current_position['end_price'] * current_position['shares']
            equity_curve.append(current_equity)

            strategy.inter_clean()
            strategy.data.end_date = today
            strategy.handle()

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
            data=strategy_class.data,
            equity_curve=equity_curve
        )


def main():
    backtester = Backtester(TWStockManager().data)

    result = backtester.run(
        stock_id='0050',
        init_funds=600000,
        strategy_class=Strategy,
        start='2015-08-01',
        # start='2015-09-04',
        # end='2015-09-10',
        end='2023-08-10',
    )
    result.show()


if __name__ == '__main__':
    main()
