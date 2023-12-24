import dataclasses

import numpy as np
import pandas as pd

from finance_bot.core.tw_stock_trade.market_data import MarketDataBase
from finance_bot.utility import Cache


@dataclasses.dataclass
class Result:
    id: int
    strategy_name: str
    params_key: str
    init_balance: int
    final_balance: int
    start_time: pd.Timestamp
    end_time: pd.Timestamp
    trade_logs: list
    market_data: MarketDataBase

    def __post_init__(self):
        self._cache = Cache()

    @property
    def trade_logs_df(self):
        return self._cache.get('trade_logs_df', self._calculate_trade_logs_df)

    @property
    def positions_df(self):
        return self._cache.get('positions_df', self._calculate_positions_df)

    @property
    def equity_curve_s(self) -> pd.Series:
        return self._cache.get('equity_curve_s', self._calculate_equity_curve_s)

    @property
    def maximum_drawdown(self) -> float:
        """MDD"""
        return self._cache.get('maximum_drawdown', self._calculate_maximum_drawdown)

    @property
    def win_rate(self) -> float:
        """勝率"""
        return self._cache.get('win_rate', self._calculate_win_rate)

    @property
    def final_equity(self) -> int:
        return self.equity_curve_s.loc[self.end_time]

    @property
    def total_return(self) -> int:
        return self._cache.get('total_return', self._calculate_total_return)

    @property
    def total_return_with_fee(self) -> int:
        return self._cache.get('total_return_with_fee', self._calculate_total_return_with_fee)

    @property
    def total_return_rate_with_fee(self) -> float:
        return self.total_return_with_fee / self.init_balance

    @property
    def annualized_return_rate_with_fee(self) -> float:
        hold_year = (self.end_time - self.start_time).days / 365.25
        return (1 + self.total_return_rate_with_fee) ** (1 / hold_year) - 1

    @property
    def avg_days(self) -> float:
        return self.positions_df.loc[self.positions_df['status'] == 'close', 'period'].mean()

    @property
    def max_days(self) -> int:
        return self.positions_df.loc[self.positions_df['status'] == 'close', 'period'].max()

    @property
    def min_days(self) -> int:
        return self.positions_df.loc[self.positions_df['status'] == 'close', 'period'].min()

    @property
    def stock_count_s(self) -> pd.Series:
        return self._cache.get('stock_count_s', self._calculate_stock_count_s)

    def _calculate_trade_logs_df(self):
        trade_logs = pd.DataFrame(self.trade_logs, columns=[
            'idx', 'date', 'action', 'stock_id', 'shares', 'fee', 'price', 'before', 'funds', 'after', 'note',
        ])
        trade_logs = trade_logs.astype({
            'idx': 'int',
            'date': 'datetime64[ns]',
            'action': 'str',
            'stock_id': 'str',
            'shares': 'int',
            'fee': 'int',
            'price': 'float',
            'before': 'int',
            'funds': 'int',
            'after': 'int',
            'note': 'str',
        })
        return trade_logs

    def _calculate_positions_df(self):
        df = self.trade_logs_df.groupby('idx').agg(
            status=('date', lambda x: 'open' if len(x) == 1 else 'close'),
            stock_id=('stock_id', 'first'),
            shares=('shares', 'first'),
            start_date=('date', 'first'),
            end_date=('date', lambda x: None if len(x) == 1 else x.iloc[-1]),
            start_price=('price', lambda x: x.iloc[0]),
            end_price=('price', lambda x: np.nan if len(x) == 1 else x.iloc[-1]),
            total_fee=('fee', 'sum'),
            note=('note', lambda x: ' | '.join(x)),
        ).reset_index()

        today_close_prices = self.market_data.close.loc[self.end_time]
        df['end_price'] = df['end_price'].fillna(df['stock_id'].map(today_close_prices))
        df['end_date'] = df['end_date'].fillna(self.end_time)

        df['period'] = (df['end_date'] - df['start_date']).dt.days
        df['total_return'] = ((df['end_price'] - df['start_price']) * df['shares']).astype(int)
        df['total_return (fee)'] = df['total_return'] - df['total_fee']

        df['total_return_rate (fee)'] = df['total_return (fee)'] / (df['start_price'] * df['shares'])  # TODO: 考慮手續費
        df['total_return_rate (fee)'] = df['total_return_rate (fee)'].apply(lambda x: f'{x * 100:.2f}%')

        df = df[[
            'status',
            'stock_id',
            'shares',
            'start_date',
            'end_date',
            'period',
            'start_price',
            'end_price',
            'total_return',
            'total_fee',
            'total_return (fee)',
            'total_return_rate (fee)',
            'note',
        ]]

        return df

    def _calculate_equity_curve_s(self) -> pd.Series:
        equity_curve = []
        balance = self.init_balance
        trade_logs_df = self.trade_logs_df

        positions = {}
        for date in self.market_data.all_date_range:
            day_trade_logs = trade_logs_df[trade_logs_df['date'] == date]

            df = day_trade_logs[day_trade_logs['action'] == 'buy']
            for _, row in df.iterrows():
                balance += row['funds']
                positions[row['idx']] = {
                    'stock_id': row['stock_id'],
                    'shares': row['shares'],
                }

            df = day_trade_logs[day_trade_logs['action'] == 'sell']
            for _, row in df.iterrows():
                balance += row['funds']
                del positions[row['idx']]

            equity = balance

            today_close_prices = self.market_data.close.loc[date]
            for position in positions.values():
                equity += today_close_prices[position['stock_id']] * position['shares']

            equity_curve.append({
                'date': date,
                'equity': equity,
            })

        return pd.Series(
            [current_equity['equity'] for current_equity in equity_curve],
            index=[current_equity['date'] for current_equity in equity_curve],
        )

    def _calculate_maximum_drawdown(self) -> float:
        """MDD"""
        running_max = self.equity_curve_s.cummax()
        drawdown = (self.equity_curve_s - running_max) / running_max
        return drawdown.min()

    def _calculate_win_rate(self) -> float:
        """勝率"""
        return (self.positions_df['total_return (fee)'] > 0).sum() / len(self.positions_df)

    def _calculate_total_return(self) -> int:
        return self.positions_df['total_return'].sum()

    def _calculate_total_return_with_fee(self) -> int:
        return self.positions_df['total_return (fee)'].sum()

    def _calculate_stock_count_s(self) -> pd.Series:
        df = self.trade_logs_df

        # 標記買入為正值，賣出為負值
        df['signed_shares'] = df.apply(lambda row: row['shares'] if row['action'] == 'buy' else -row['shares'], axis=1)

        # 按股票 ID 和日期分組，計算每個股票的累積持股數量
        cumulative_shares = df.groupby(['stock_id', 'date']).sum()['signed_shares'].groupby(
            level=0).cumsum().reset_index()

        # 為了得到每天的數據，創建一個所有日期的範圍
        all_dates = pd.date_range(start=df['date'].min(), end=df['date'].max())

        # 對每個股票，擴展到每日數據
        all_stocks_daily = cumulative_shares.pivot(index='date', columns='stock_id', values='signed_shares')
        all_stocks_daily = all_stocks_daily.reindex(all_dates).ffill().fillna(0)

        # 篩選出持有的股票
        all_stocks_daily = all_stocks_daily[all_stocks_daily > 0]

        # 計算每天持有的股票種類數量
        return all_stocks_daily.gt(0).sum(axis=1)
