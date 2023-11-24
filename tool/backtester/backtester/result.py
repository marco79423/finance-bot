import dataclasses

import pandas as pd


@dataclasses.dataclass
class Result:
    id: int
    strategy_name: str
    max_single_position_exposure: float
    init_funds: int
    final_funds: int
    start_time: pd.Timestamp
    end_time: pd.Timestamp
    trade_logs: pd.DataFrame
    trades: pd.DataFrame
    equity_curve: pd.Series

    @property
    def final_equity(self):
        return self.equity_curve.loc[self.end_time]

    @property
    def total_return(self):
        return self.trades['total_return'].sum()

    @property
    def total_return_with_fee(self):
        return self.trades['total_return (fee)'].sum()

    @property
    def total_return_rate_with_fee(self):
        return self.total_return_with_fee / self.init_funds

    @property
    def annualized_return_rate_with_fee(self):
        hold_year = (self.end_time - self.start_time).days / 365.25
        return (1 + self.total_return_rate_with_fee) ** (1 / hold_year) - 1

    @property
    def avg_days(self):
        return self.trades['period'].mean()

    @property
    def max_days(self):
        return self.trades['period'].max()

    @property
    def min_days(self):
        return self.trades['period'].min()

    def detail(self, with_trades=False, with_trade_logs=False):
        print(f'使用策略 {self.strategy_name} 回測結果')
        print(f'回測範圍： {self.start_time} ~ {self.end_time}')
        print(f'原始本金： {self.init_funds} 元')
        print(f'最終本金： {self.final_funds}')
        print(f'最終權益： {self.final_equity} 元')
        print(f'總獲利： {self.total_return} 元')
        print(f'總獲利(含手續費)： {self.total_return_with_fee} 元')
        print(f'平均天數： {self.avg_days:.1f} 天 (最長: {self.max_days:.1f} 天, 最短: {self.min_days:.1f}) 天')
        print(f'報酬率： {self.total_return_rate_with_fee * 100:.2f}%')
        print(f'年化報酬率(含手續費)： {self.annualized_return_rate_with_fee * 100:.2f}%')

        if with_trades:
            print(f'各倉位狀況：')
            with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None):
                print(self.trades)

        if with_trade_logs:
            print(f'交易紀錄：')
            with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None):
                print(self.trade_logs)
