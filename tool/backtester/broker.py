import math

import pandas as pd

from tool.backtester.model import LimitMarketData


class Broker:
    fee_discount = 0.6
    fee_rate = 1.425 / 1000 * fee_discount  # 0.1425％
    tax_rate = 3 / 1000  # 政府固定收 0.3 %

    def __init__(self, data, init_funds, max_single_position_exposure):
        self._data = data
        self._funds = init_funds
        self._max_single_position_exposure = max_single_position_exposure

        self._current_idx = 0
        self._start_date = None
        self._current_date = None
        self._open_trades = {}
        self._close_trades = []
        self._equity_curve = []

        self._all_close_prices = self._data.close.ffill()  # 補完空值的收盤價
        self._all_high_prices = self._data.high.ffill()  # 補完空值的最高價
        self._all_low_prices = self._data.low.ffill()  # 補完空值的最低價

        self._stock_data_cache = {}

    def stock_data(self, stock_id):
        if stock_id not in self._stock_data_cache:
            self._stock_data_cache[stock_id] = LimitMarketData(
                self._data[stock_id],
                start_date=self._start_date,
                end_date=self._current_date,
            )
        self._stock_data_cache[stock_id].end_date = self._current_date
        return self._stock_data_cache[stock_id]

    def begin_date(self, date):
        if self._start_date is None:
            self._start_date = date
        self._current_date = date

    def end_date(self):
        self._equity_curve.append({
            'date': self._current_date,
            'equity': self.current_equity
        })

    def buy(self, stock_id, note=''):
        # 回測使用當日最高價買入
        entry_price = self._get_stock_high_price(stock_id)

        shares = int((self.single_entry_limit / (entry_price * (1 + self.fee_rate)) // 1000) * 1000)
        if shares < 1000:
            return False

        fee = max(math.floor(shares * entry_price * self.fee_rate), 1)  # 永豐說是無條件捨去，最低收 1 元
        close_price = self._get_stock_close_price(stock_id)  # 因為是回測，預先就知道收盤價
        self._open_trades[stock_id] = {
            'idx': self._current_idx,
            'status': 'open',
            'stock_id': stock_id,
            'shares': shares,
            'start_date': self._current_date,
            'start_price': entry_price,
            'end_date': self._current_date,
            'end_price': close_price,
            'total_fee': fee,
            'total_return (fee)': (close_price - entry_price) * shares - fee,
            'note': f'buy: {note}',
        }
        self._current_idx += 1

        self._funds -= shares * entry_price + fee
        return True

    def sell(self, stock_id, note):
        if stock_id not in self._open_trades:
            return False

        # 回測使用當日最低價賣出
        price = self._get_stock_low_price(stock_id)

        trade = self._open_trades[stock_id]
        fee = max(math.floor(trade['shares'] * trade['end_price'] * (self.fee_rate * self.tax_rate)), 1)
        total_fee = trade['total_fee'] + fee
        trade = {
            **trade,
            'status': 'close',
            'end_date': self._current_date,
            'end_price': price,
            'total_fee': total_fee,
            'total_return (fee)': (price - trade['start_price']) * trade['shares'] - total_fee,
            'note': trade['note'] + f'| sell: {note}',
        }
        self._close_trades.append(trade)

        self._funds += trade['shares'] * trade['end_price'] - fee

        del self._open_trades[stock_id]
        return True

    @property
    def current_date(self):
        return self._current_date

    @property
    def single_entry_limit(self):
        invested_funds = sum(trade['start_price'] * trade['shares'] for trade in self._open_trades)
        return math.floor((invested_funds + self.funds) * self._max_single_position_exposure)

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

        today_close_prices = self._all_close_prices.loc[self._current_date]
        df['end_price'].update(df['stock_id'].map(today_close_prices))

        df['total_return (fee)'] = (df['end_price'] - df['start_price']) * df['shares'] - df['total_fee']
        return df

    @property
    def close_trades(self):
        if not self._close_trades:
            return self._create_empty_trades()
        return pd.DataFrame(self._close_trades).set_index('idx').sort_index()

    @property
    def all_trades(self):
        return pd.concat([self.close_trades, self.open_trades]).sort_index()

    @property
    def equity_curve(self):
        return pd.Series(
            [current_equity['equity'] for current_equity in self._equity_curve],
            index=[current_equity['date'] for current_equity in self._equity_curve],
        )

    def _get_stock_high_price(self, stock_id):
        return self._all_high_prices.loc[self._current_date, stock_id]

    def _get_stock_low_price(self, stock_id):
        return self._all_low_prices.loc[self._current_date, stock_id]

    def _get_stock_close_price(self, stock_id):
        return self._all_close_prices.loc[self._current_date, stock_id]

    @staticmethod
    def _create_empty_trades():
        return pd.DataFrame(
            columns=[
                'status',

                'stock_id',
                'shares',

                'start_date',
                'start_price',

                'end_date',
                'end_price',

                'total_fee',
                'total_return (fee)',
                'note',
            ])
