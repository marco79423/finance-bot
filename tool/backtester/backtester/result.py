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
    positions: pd.DataFrame
    equity_curve: pd.Series

    @property
    def final_equity(self):
        return self.equity_curve.loc[self.end_time]

    @property
    def total_return(self):
        return self.positions['total_return'].sum()

    @property
    def total_return_with_fee(self):
        return self.positions['total_return (fee)'].sum()

    @property
    def total_return_rate_with_fee(self):
        return self.total_return_with_fee / self.init_funds

    @property
    def annualized_return_rate_with_fee(self):
        hold_year = (self.end_time - self.start_time).days / 365.25
        return (1 + self.total_return_rate_with_fee) ** (1 / hold_year) - 1

    @property
    def avg_days(self):
        return self.positions['period'].mean()

    @property
    def max_days(self):
        return self.positions['period'].max()

    @property
    def min_days(self):
        return self.positions['period'].min()
