import math

import pandas as pd


class Broker:
    fee_discount = 0.6
    fee_rate = 1.425 / 1000 * fee_discount  # 0.1425％
    tax_rate = 3 / 1000  # 政府固定收 0.3 %

    def __init__(self, data, init_balance, max_single_position_exposure):
        self._data = data
        self._init_balance = init_balance
        self._balance = init_balance
        self._max_single_position_exposure = max_single_position_exposure

        self._current_idx = 0
        self._positions = {}
        self._trade_logs = []

    def buy(self, stock_id, note=''):
        # 回測使用當日最高價買入
        entry_price = self._data.get_stock_high_price(stock_id)

        shares = int((self.single_entry_limit / (entry_price * (1 + self.fee_rate)) // 1000) * 1000)
        if shares < 1000:
            return False

        before = self.balance
        fee = max(math.floor(shares * entry_price * self.fee_rate), 1)  # 永豐說是無條件捨去，最低收 1 元
        funds = int(shares * entry_price) + fee
        after = before - funds

        # 先寫 log
        self._trade_logs.append({
            'idx': self._current_idx,
            'date': self._data.current_time,
            'action': 'buy',
            'stock_id': stock_id,
            'shares': shares,
            'fee': fee,
            'price': entry_price,
            'before': before,
            'funds': -funds,
            'after': after,
            'note': note,
        })

        # 執行交易
        if stock_id not in self._positions:
            self._positions[stock_id] = {}

        self._positions[stock_id][self._current_idx] = {
            'idx': self._current_idx,
            'stock_id': stock_id,
            'shares': shares,
            'start_date': self._data.current_time,
            'start_price': entry_price,
        }
        self._balance = after
        self._current_idx += 1

        return True

    def sell(self, stock_id, note):
        if stock_id not in self._positions:
            return False

        # 回測使用當日最低價賣出
        price = self._data.get_stock_low_price(stock_id)

        for position in self._positions[stock_id].values():
            before = self.balance
            fee = max(math.floor(position['shares'] * price * (self.fee_rate + self.tax_rate)), 1)
            funds = int(position['shares'] * price) - fee
            after = before + funds

            # 先寫 log
            self._trade_logs.append({
                'idx': position['idx'],
                'date': self._data.current_time,
                'action': 'sell',
                'stock_id': stock_id,
                'shares': position['shares'],
                'fee': fee,
                'price': price,
                'before': before,
                'funds': funds,
                'after': after,
                'note': note,
            })

            # 執行交易
            self._balance = after

        del self._positions[stock_id]

        return True

    @property
    def invested_funds(self):
        funds = 0
        for positions in self._positions.values():
            for position in positions.values():
                funds += int(position['start_price'] * position['shares'])
        return funds

    @property
    def single_entry_limit(self):
        return min(math.floor((self.invested_funds + self.balance) * self._max_single_position_exposure), self.balance)

    @property
    def init_balance(self):
        return self._init_balance

    @property
    def balance(self):
        return self._balance

    @property
    def holding_stock_ids(self):
        return list(self._positions.keys())

    @property
    def current_shares(self):
        items = []
        for stock_id, positions in self._positions.items():
            items.append({
                'stock_id': stock_id,
                'shares': sum(position['shares'] for position in positions.values())
            })
        return pd.Series(
            [item['shares'] for item in items],
            index=[item['stock_id'] for item in items],
        )

    def get_entry_date(self, stock_id):
        for position in self._positions[stock_id].values():
            return position['start_date']

    @property
    def entry_date(self):
        items = []
        for stock_id in self._positions:
            items.append({
                'stock_id': stock_id,
                'entry_date': self.get_entry_date(stock_id)
            })
        return pd.Series(
            [item['entry_date'] for item in items],
            index=[item['stock_id'] for item in items],
        )

    def get_entry_price(self, stock_id):
        for position in self._positions[stock_id].values():
            return position['start_price']

    @property
    def entry_price(self):
        items = []
        for stock_id in self._positions:
            items.append({
                'stock_id': stock_id,
                'entry_price': self.get_entry_price(stock_id),
            })
        return pd.Series(
            [item['entry_price'] for item in items],
            index=[item['stock_id'] for item in items],
        )

    @property
    def break_even_price(self):
        fee_ratio = 1.425 / 1000 * self.fee_discount  # 0.1425％
        tax_ratio = 3 / 1000  # 政府固定收 0.3 %
        return self.entry_price * (1 + fee_ratio) / (1 - fee_ratio - tax_ratio)

    def get_open_trades_by_stock_id(self, stock_id):
        return self._positions.get(stock_id, None)

    @property
    def trade_logs(self):
        return self._trade_logs
