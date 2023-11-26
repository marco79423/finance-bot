import datetime as dt
import dataclasses
from typing import Optional

import pandas as pd

from finance_bot.core.tw_stock_legacy.strategy import FinlabStrategy
from finance_bot.core.tw_stock_legacy.strategy.base import StrategyBase
from finance_bot.core.tw_stock_legacy.ticker_db.ticker_db import Ticker, TickerDB


@dataclasses.dataclass
class Position:
    """投資部位"""
    shares: int
    start_date: pd.Timestamp
    start_price: float
    end_date: Optional[pd.Timestamp] = None
    end_price: Optional[float] = None
    max_price: Optional[float] = None
    min_price: Optional[float] = None

    def get_total_return(self) -> float:
        return (self.end_price - self.start_price) * self.shares

    def get_holding_period(self) -> pd.Timedelta:
        return self.end_date - self.start_date

    def get_return_rate(self) -> float:
        return (self.end_price - self.start_price) / self.start_price

    def get_max_return_rate(self) -> float:
        return (self.max_price - self.start_price) / self.start_price

    def get_min_return_rate(self) -> float:
        return (self.min_price - self.start_price) / self.start_price


@dataclasses.dataclass
class BacktestReport:
    strategy_name: str
    ticker_symbol: str
    start_date: dt.datetime
    end_date: dt.datetime
    init_funds: float
    positions: [Position]
    total_assets_per_date: pd.Series

    def get_total_return(self) -> float:
        return sum(position.get_total_return() for position in self.positions)

    def get_total_holding_period(self) -> pd.Timedelta:
        return pd.Series(position.get_holding_period() for position in self.positions).sum()

    def get_avg_holding_period_per_position(self) -> pd.Timedelta:
        return self.get_total_holding_period() / len(self.positions)

    def get_max_holding_period_per_position(self) -> pd.Timedelta:
        return max(position.get_holding_period() for position in self.positions)

    def get_min_holding_period_per_position(self) -> pd.Timedelta:
        return min(position.get_holding_period() for position in self.positions)

    def get_avg_return_rate_per_position(self) -> float:
        return sum(position.get_return_rate() for position in self.positions) / len(self.positions)

    def get_max_return_rate_per_position(self) -> float:
        return max(position.get_max_return_rate() for position in self.positions)

    def get_min_return_rate_per_position(self) -> float:
        return min(position.get_min_return_rate() for position in self.positions)

    def stats(self):
        print(f'{self.ticker_symbol} 使用策略 {self.strategy_name} 回測結果')
        print(f'回策時間範圍 {self.start_date} ~ {self.end_date}')
        print(f'原始本金： {self.init_funds} 總獲利： {self.get_total_return()}')
        print(f'各倉位狀況：')
        for position in self.positions:
            time = f'{position.start_time.date()} ~ {position.settle_date.date()}'
            period = position.get_holding_period()
            shares = position.shares
            start_price = position.start_price
            end_price = position.end_price
            total_return = position.get_total_return()

            return_rate = position.get_return_rate()
            max_return_rate = position.get_max_return_rate()
            min_return_rate = position.get_min_return_rate()

            print(
                f'[{time} (持有： {period.total_seconds() / 86400} 天)] 持股: {shares} 初始價: {start_price:.2f} 最終價： {end_price:.2f} 總獲利： {total_return:.2f} 收益率: {return_rate * 100:.2f}% (最高： {max_return_rate * 100}%, 最低： {min_return_rate * 100:.2f}%)')
        print(f'各倉位統計：')
        print(
            f'平圴收益率： {self.get_avg_return_rate_per_position() * 100:.2f}% (最高： {self.get_max_return_rate_per_position() * 100:.2f}%, 最低： {self.get_min_return_rate_per_position() * 100 :.2f}%)')
        print(
            f'平圴時長： {self.get_avg_holding_period_per_position().total_seconds() / 86400} 天 (最高： {self.get_max_holding_period_per_position().total_seconds() / 86400:.2f} 天, 最低： {self.get_min_holding_period_per_position().total_seconds() / 86400:.2f} 天)')


def backtest_for_single_ticker(init_funds, ticker: Ticker, strategy: StrategyBase, max_holdings=None, fee_discount=0.6):
    # 手續費和稅的比例
    fee_rate = 1.425 / 1000 * fee_discount  # 0.1425％
    tax_rate = 3 / 1000  # 政府固定收 0.3 %

    # 初始化資金和股票數量
    funds = init_funds
    shares = 0

    # 獲取股票的收盤價
    close_prices = ticker.get_close_prices()

    # 初始化當前持有期間
    total_assets_per_date = pd.Series(name='total_assets')
    close_positions = []
    positions = []

    # 遍歷每一天
    for date, price in close_prices.items():
        if strategy.is_sell_point(ticker.symbol, date) or close_prices.index[-1] == date:
            for position in positions:
                # 更新資訊
                position.end_date = date
                position.end_price = price
                position.max_price = close_prices[position.start_date: date].max()
                position.min_price = close_prices[position.start_date: date].min()

                # 更新資金和股票數量
                funds += position.shares * price * (1 - fee_rate - tax_rate)
                shares -= position.shares

            close_positions = close_positions + positions
            positions = []

        # 如果今天是買入的時間點，並且持有的股票數量小於最大持有數量
        if funds > price and strategy.is_buy_point(ticker.symbol, date) and close_prices.index[-1] != date:
            # 計算可以買入的股票數量
            buy_shares = funds // price
            if max_holdings:
                buy_shares = max(min(buy_shares, max_holdings - shares), 0)

            if buy_shares > 0:
                # 更新資金和股票數量
                funds -= price * buy_shares * (1 + fee_rate)
                shares += buy_shares

                # 開始新的持有期間
                positions.append(Position(
                    shares=buy_shares,
                    start_date=date,
                    start_price=price,
                ))

        total_assets_per_date[date] = funds + sum(position.shares for position in positions) * price

    # 創建回測報告
    return BacktestReport(
        strategy_name=strategy.name,
        ticker_symbol=ticker.symbol,
        start_date=close_prices.index[0],
        end_date=close_prices.index[-1],
        init_funds=init_funds,
        positions=close_positions + positions,
        total_assets_per_date=total_assets_per_date,
    )


if __name__ == '__main__':
    ticker_db = TickerDB()
    # strategy = Always0050Strategy(ticker_db)
    strategy = FinlabStrategy(ticker_db)

    tickers = strategy.select_tickers(dt.datetime(year=2020, month=12, day=1))
    report = backtest_for_single_ticker(
        init_funds=300000,
        ticker=tickers[0],
        strategy=strategy,
    )

    report.stats()
