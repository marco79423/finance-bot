import math

import pandas as pd


class Broker:
    fee_discount = 0.6
    fee_rate = 1.425 / 1000 * fee_discount  # 0.1425％
    tax_rate = 3 / 1000  # 政府固定收 0.3 %

    def __init__(self, data, init_funds, max_single_position_exposure):
        self._data = data
        self._init_funds = init_funds
        self._funds = init_funds
        self._max_single_position_exposure = max_single_position_exposure

        self._current_idx = 0
        self._open_trades = {}
        self._close_trades = []
        self._equity_curve = []
        self._trade_logs = []

    def settle_date(self):
        self._equity_curve.append({
            'date': self._data.current_time,
            'equity': self.current_equity
        })

    def buy(self, stock_id, note=''):
        # 回測使用當日最高價買入
        entry_price = self._data.get_stock_high_price(stock_id)

        shares = int((self.single_entry_limit / (entry_price * (1 + self.fee_rate)) // 1000) * 1000)
        if shares < 1000:
            return False

        fee = max(math.floor(shares * entry_price * self.fee_rate), 1)  # 永豐說是無條件捨去，最低收 1 元
        close_price = self._data.get_stock_close_price(stock_id)  # 因為是回測，預先就知道收盤價
        entry_funds = shares * entry_price + fee

        self._open_trades[stock_id] = {
            'idx': self._current_idx,
            'status': 'open',
            'stock_id': stock_id,
            'shares': shares,
            'start_date': self._data.current_time,
            'start_price': entry_price,
            'end_date': self._data.current_time,
            'end_price': close_price,
            'total_fee': fee,
            'note': f'buy: {note}',
        }
        self._current_idx += 1

        before = self.funds
        self._funds -= entry_funds

        self._trade_logs.append({
            'date': self._data.current_time,
            'action': 'buy',
            'stock_id': stock_id,
            'before': before,
            'funds': -entry_funds,
            'after': self.funds,
            'note': note,
        })

        return True

    def sell(self, stock_id, note):
        if stock_id not in self._open_trades:
            return False

        # 回測使用當日最低價賣出
        price = self._data.get_stock_low_price(stock_id)

        trade = self._open_trades[stock_id]
        fee = max(math.floor(trade['shares'] * trade['end_price'] * (self.fee_rate * self.tax_rate)), 1)
        total_fee = trade['total_fee'] + fee
        exit_funds = trade['shares'] * trade['end_price'] - fee

        trade = {
            **trade,
            'status': 'close',
            'end_date': self._data.current_time,
            'end_price': price,
            'total_fee': total_fee,
            'note': trade['note'] + f'| sell: {note}',
        }
        self._close_trades.append(trade)

        before = self.funds
        self._funds += exit_funds

        del self._open_trades[stock_id]

        self._trade_logs.append({
            'date': self._data.current_time,
            'action': 'sell',
            'stock_id': stock_id,
            'before': before,
            'funds': exit_funds,
            'after': self.funds,
            'note': note,
        })

        return True

    @property
    def single_entry_limit(self):
        invested_funds = sum(trade['start_price'] * trade['shares'] for trade in self._open_trades.values())
        return min(math.floor((invested_funds + self.funds) * self._max_single_position_exposure), self.funds)

    @property
    def init_funds(self):
        return self._init_funds

    @property
    def funds(self):
        return self._funds

    @property
    def current_equity(self):
        return self.funds + (self.open_trades['end_price'] * self.open_trades['shares']).sum()

    @property
    def holding_stock_ids(self):
        return list(self._open_trades.keys())

    @property
    def open_trades(self):
        if not self._open_trades:
            return self._create_empty_trades()

        df = pd.DataFrame(self._open_trades.values()).set_index('idx').sort_index()

        today_close_prices = self._data.all_close.loc[self._data.current_time]
        df['end_price'].update(df['stock_id'].map(today_close_prices))
        return df

    def get_open_trades_by_stock_id(self, stock_id):
        return self._open_trades.get(stock_id, None)

    @property
    def close_trades(self):
        if not self._close_trades:
            return self._create_empty_trades()
        return pd.DataFrame(self._close_trades).set_index('idx').sort_index()

    @property
    def all_trades(self):
        df = None
        if not self.close_trades.empty:
            df = self.close_trades

        if not self.open_trades.empty:
            if df is None:
                df = self.open_trades
            else:
                df = pd.concat([df, self.open_trades]).sort_index()

        if df is None:
            df = self._create_empty_trades()

        return df

    @property
    def trade_logs(self):
        if not self._trade_logs:
            return self._create_empty_trades_logs()
        return pd.DataFrame(self._trade_logs)

    @property
    def analysis_trades(self):
        df = self.all_trades
        df['period'] = (df['end_date'] - df['start_date']).dt.days

        df['total_return'] = ((df['end_price'] - df['start_price']) * df['shares']).astype(int)
        df['total_return (fee)'] = df['total_return'] - df['total_fee']
        df['total_return_rate (fee)'] = df['total_return (fee)'] / (df['start_price'] * df['shares'])  # TODO: 考慮手續費
        return df

    @property
    def equity_curve(self):
        return pd.Series(
            [current_equity['equity'] for current_equity in self._equity_curve],
            index=[current_equity['date'] for current_equity in self._equity_curve],
        )

    @property
    def total_return(self):
        return self.analysis_trades['total_return'].sum()

    @property
    def total_return_with_fee(self):
        return self.analysis_trades['total_return (fee)'].sum()

    @property
    def total_return_rate_with_fee(self):
        return self.total_return_with_fee / self.init_funds

    @property
    def annualized_return_rate_with_fee(self):
        hold_year = (self._data.current_time - self._data.start_time).days / 365.25
        return (1 + self.total_return_rate_with_fee) ** (1 / hold_year) - 1

    @staticmethod
    def _create_empty_trades():
        return pd.DataFrame({
            'status': pd.Series(dtype='str'),

            'stock_id': pd.Series(dtype='str'),
            'shares': pd.Series(dtype='int'),

            'start_date': pd.Series(dtype='datetime64[ns]'),
            'start_price': pd.Series(dtype='float'),

            'end_date': pd.Series(dtype='datetime64[ns]'),
            'end_price': pd.Series(dtype='float'),

            'total_fee': pd.Series(dtype='float'),
            'note': pd.Series(dtype='str'),
        })

    @staticmethod
    def _create_empty_trades_logs():
        return pd.DataFrame({
            'date': pd.Series(dtype='datetime64[ns]'),
            'action': pd.Series(dtype='str'),
            'stock_id': pd.Series(dtype='str'),
            'before': pd.Series(dtype='float'),
            'funds': pd.Series(dtype='float'),
            'after': pd.Series(dtype='float'),
            'note': pd.Series(dtype='str'),
        })
