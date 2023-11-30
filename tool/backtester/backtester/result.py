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
    def maximum_drawdown(self):
        """MDD"""
        running_max = self.equity_curve.cummax()
        drawdown = (self.equity_curve - running_max) / running_max
        return drawdown.min()

    @property
    def win_rate(self):
        """勝率"""
        return (self.positions['total_return (fee)'] > 0).sum() / len(self.positions)

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
        return self.positions.loc[self.positions['status'] == 'close', 'period'].mean()

    @property
    def max_days(self):
        return self.positions.loc[self.positions['status'] == 'close', 'period'].max()

    @property
    def min_days(self):
        return self.positions.loc[self.positions['status'] == 'close', 'period'].min()

    @property
    def stock_count(self):
        df = self.trade_logs

        # 標記買入為正值，賣出為負值
        df['signed_shares'] = df.apply(lambda row: row['shares'] if row['action'] == 'buy' else -row['shares'], axis=1)

        # 按股票 ID 和日期分組，計算每個股票的累積持股數量
        cumulative_shares = df.groupby(['stock_id', 'date']).sum()['signed_shares'].groupby(level=0).cumsum().reset_index()

        # 為了得到每天的數據，創建一個所有日期的範圍
        all_dates = pd.date_range(start=df['date'].min(), end=df['date'].max())

        # 對每個股票，擴展到每日數據
        all_stocks_daily = cumulative_shares.pivot(index='date', columns='stock_id', values='signed_shares')
        all_stocks_daily = all_stocks_daily.reindex(all_dates).ffill().fillna(0)

        # 篩選出持有的股票
        all_stocks_daily = all_stocks_daily[all_stocks_daily > 0]

        # 計算每天持有的股票種類數量
        return all_stocks_daily.gt(0).sum(axis=1)
