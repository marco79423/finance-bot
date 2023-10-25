import math

import pandas as pd

from finance_bot.core.tw_stock_manager.data_getter import DataGetter


class Broker:
    fee_discount = 0.6
    fee_rate = 1.425 / 1000 * fee_discount  # 0.1425％
    tax_rate = 3 / 1000  # 政府固定收 0.3 %

    _data: DataGetter

    def __init__(self, init_funds, max_single_position_exposure):
        self._funds = init_funds
        self._max_single_position_exposure = max_single_position_exposure

        self._current_idx = 0
        self._open_trades = {}
        self._close_trades = []

    def buy(self, date, stock_id, price):
        shares = int((self.single_entry_limit / (price * (1 + self.fee_rate)) // 1000) * 1000)
        if shares < 1000:
            return False

        self._open_trades[stock_id] = {
            'idx': self._current_idx,
            'status': 'open',
            'stock_id': stock_id,
            'shares': shares,
            'start_date': date,
            'start_price': price,
            'end_date': date,
            'end_price': price,
        }
        self._current_idx += 1

        fee = math.floor(shares * price * self.fee_rate)  # 永豐說是無條件捨去，最低收 1 元
        if fee == 0:
            fee = 1

        self._funds -= shares * price + fee
        return True

    def sell(self, date, stock_id, price):
        if stock_id not in self._open_trades:
            return False

        trade = self._open_trades[stock_id]
        trade = {
            **trade,
            'status': 'close',
            'end_date': date,
            'end_price': price,
        }
        self._close_trades.append(trade)

        fee = math.floor(trade['shares'] * trade['end_price'] * (self.fee_rate * self.tax_rate))
        if fee == 0:
            fee = 1
        self._funds += trade['shares'] * trade['end_price'] - fee

        del self._open_trades[stock_id]
        return True

    @property
    def single_entry_limit(self):
        invested_funds = sum(trade['start_price'] * trade['shares'] for trade in self._open_trades)
        return math.floor((invested_funds + self.funds) * self._max_single_position_exposure)

    @property
    def funds(self):
        return self._funds

    @property
    def holding_stock_ids(self):
        return list(self._open_trades.keys())

    @property
    def open_trades(self):
        if not self._open_trades:
            return pd.DataFrame(columns=['status', 'stock_id', 'shares', 'start_date', 'start_price', 'end_date', 'end_price'])
        return pd.DataFrame(self._open_trades.values()).set_index('idx').sort_index()

    @property
    def close_trades(self):
        if not self._close_trades:
            return pd.DataFrame(columns=['status', 'stock_id', 'shares', 'start_date', 'start_price', 'end_date', 'end_price'])
        return pd.DataFrame(self._close_trades).set_index('idx').sort_index()

    @property
    def all_trades(self):
        return pd.concat([self.close_trades, self.open_trades]).sort_index()
