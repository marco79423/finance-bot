import dataclasses
import math
from typing import Optional

import pandas as pd
import plotly.express as px

from finance_bot.core import TWStockManager
from tool.backtester.model import LimitData
from tool.backtester.strategy import SimpleStrategy


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


class MultiStocksBacktester:
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

    def run(self, init_funds, max_single_position_exposure, strategy_class, start, end):
        start = pd.Timestamp(start)
        end = pd.Timestamp(end)

        all_close_prices = self.data.close.ffill()  # 補完空值的收盤價
        all_high_prices = self.data.high.ffill()  # 補完空值的最高價
        all_low_prices = self.data.low.ffill()  # 補完空值的最低價

        strategy_class.data = self.data

        strategy_map = {}

        all_stock_ids = strategy_class.available_stock_ids
        if not all_stock_ids:
            all_stock_ids = all_close_prices.columns

        for stock_id in all_stock_ids:
            strategy = strategy_class()
            strategy.data = LimitData(self.data[stock_id])
            strategy_map[stock_id] = strategy

        # 手續費和稅的比例
        fee_rate = 1.425 / 1000 * self.fee_discount  # 0.1425％
        tax_rate = 3 / 1000  # 政府固定收 0.3 %

        # 初始化資金和股票數量
        funds = init_funds
        trades = pd.DataFrame(
            columns=['status', 'stock_id', 'shares', 'start_date', 'start_price', 'end_date', 'end_price'])

        all_date_range = all_close_prices.loc[start:end].index  # 交易日

        equity_curve = []
        for today in all_date_range:
            today_high_prices = all_high_prices.loc[today]
            today_low_prices = all_low_prices.loc[today]
            today_close_prices = all_close_prices.loc[today]

            single_entry_limit = math.floor(
                (trades.loc[trades['status'] == 'open', 'start_price'].sum() + funds) * max_single_position_exposure)
            holding_stock_ids = trades.loc[trades['status'] == 'open', 'stock_id']

            if (trades['status'] == 'open').any():
                trades['end_price'].update(trades.loc[trades['status'] == 'open', 'stock_id'].map(today_close_prices))
                trades.loc[trades['status'] == 'open', 'end_date'] = today

                sell_stock_ids = []
                for stock_id, strategy in strategy_map.items():
                    if strategy._sell_next_day_market:
                        sell_stock_ids.append(stock_id)

                if sell_stock_ids:
                    open_cond = trades['status'] == 'open'
                    sell_ids_cond = trades['stock_id'].isin(sell_stock_ids)
                    new_close_positions = trades.loc[open_cond & sell_ids_cond]

                    fee = math.floor(
                        sum(new_close_positions['shares'] * new_close_positions['end_price'] * (fee_rate * tax_rate)))
                    funds += sum(new_close_positions['shares'] * new_close_positions['end_price']) - fee

                    trades['end_price'].update(trades.loc[open_cond & sell_ids_cond, 'stock_id'].map(today_low_prices))
                    trades.loc[open_cond & sell_ids_cond, 'end_date'] = today
                    trades.loc[open_cond & sell_ids_cond, 'status'] = 'close'

            available_stock_ids = []
            for stock_id, strategy in strategy_map.items():
                if strategy._buy_next_day_market and stock_id not in holding_stock_ids:
                    available_stock_ids.append(stock_id)

            new_positions = []
            for stock_id in available_stock_ids:
                high_price = today_high_prices[stock_id]

                shares = int((single_entry_limit / (high_price * (1 + fee_rate)) // 1000) * 1000)
                if shares < 1000:
                    continue

                new_positions.append({
                    'status': 'open',
                    'stock_id': stock_id,
                    'shares': shares,
                    'start_date': today,
                    'start_price': high_price,
                    'end_price': today_close_prices[stock_id],
                    'end_date': today,
                })
                funds -= shares * (high_price * (1 + fee_rate))
            new_positions = pd.DataFrame(new_positions)

            trades = pd.concat([trades, new_positions])
            trades = trades.reset_index(drop=True)

            open_positions = trades.loc[trades['status'] == 'open']
            current_equity = funds + sum(open_positions['end_price'] * open_positions['shares'])
            equity_curve.append(current_equity)

            for _, strategy in strategy_map.items():
                strategy.inter_clean()
                strategy.data.end_date = today
                strategy.handle()

        equity_curve = pd.Series(equity_curve, index=all_date_range)
        return Result(
            strategy_name=strategy_class.name,
            start=start,
            end=end,
            init_funds=init_funds,
            final_funds=funds,
            trades=trades,
            equity_curve=equity_curve
        )


def main():
    backtester = MultiStocksBacktester(TWStockManager().data)

    result = backtester.run(
        init_funds=600000,
        # max_single_position_exposure=0.1,
        max_single_position_exposure=1,
        strategy_class=SimpleStrategy,
        start='2015-08-01',
        end='2023-08-10',
    )
    result.show()


if __name__ == '__main__':
    main()
