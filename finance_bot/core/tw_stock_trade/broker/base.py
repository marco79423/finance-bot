import abc
import dataclasses
import math

import pandas as pd

from finance_bot.infrastructure import infra


@dataclasses.dataclass
class Position:
    entry_date: pd.Timestamp
    stock_id: str
    avg_price: float
    shares: int

    def increase(self, shares, price):
        self.avg_price = (self.avg_price * self.shares + shares * price) / (self.shares + shares)
        self.shares += shares

    def decrease(self, shares, price):
        self.avg_price = (self.avg_price * self.shares - shares * price) / (self.shares - shares)
        self.shares -= shares


@dataclasses.dataclass
class CommissionInfo:
    fee_discount: float = 1  # 永豐是月退，當沒打折

    @property
    def fee_rate(self):
        return 1.425 / 1000 * self.fee_discount  # 0.1425％

    @property
    def tax_rate(self):
        return 3 / 1000  # 政府固定收 0.3 %

    def get_buy_commission(self, price, shares) -> int:
        commission = max(math.floor(shares * price * self.fee_rate), 1)  # 無條件捨去小數點，但最低是 1 元
        return commission

    def get_sell_commission(self, price, shares) -> int:
        commission = max(math.floor(shares * price * self.fee_rate), 1)  # 無條件捨去小數點，但最低是 1 元
        commission += math.floor(shares * price * self.tax_rate)  # 無條件捨去小數點
        return commission


class BrokerBase(abc.ABC):
    name = 'broker_base'

    commission_info = CommissionInfo(fee_discount=1)

    def __init__(self):
        self.logger = infra.logger.bind(name=self.name)
        self._cache = {}

    ################
    #      操作
    ################

    def refresh(self):
        self._cache = {}

    @abc.abstractmethod
    def buy_market(self, stock_id, shares, note=''):
        """發現沒錢就自動放棄購買"""
        pass

    @abc.abstractmethod
    def sell_all_market(self, stock_id, note=''):
        pass

    ################
    #      狀態
    ################

    def get_current_balance(self):
        pass

    def get_positions(self) -> [Position]:
        pass

    @property
    def current_balance(self):
        if 'current_balance' not in self._cache:
            self._cache['current_balance'] = self.get_current_balance()
        return self._cache['current_balance']

    @property
    def positions(self) -> [Position]:
        if 'positions' not in self._cache:
            self._cache['positions'] = self.get_positions()
        return self._cache['positions']

    ################
    #      統計
    ################

    @property
    def holding_stock_ids(self) -> [str]:
        """當前持有的股票代碼列表"""
        if 'holding_stock_ids' not in self._cache:
            stock_ids = []
            for position in self.positions:
                stock_ids.append(position.stock_id)
            self._cache['holding_stock_ids'] = stock_ids
        return self._cache['holding_stock_ids']

    @property
    def holding_stock_entry_date_s(self) -> pd.Series:
        """當前持有的股票入場時間"""
        if 'holding_stock_entry_date_s' not in self._cache:
            stock_entry_date_map = {}
            for position in self.positions:
                if position.stock_id not in stock_entry_date_map:
                    stock_entry_date_map[position.stock_id] = position.entry_date

            self._cache['holding_stock_entry_date_s'] = pd.Series(
                [stock_entry_date_map[stock_id] for stock_id in self.holding_stock_ids],
                index=self.holding_stock_ids,
            )
        return self._cache['holding_stock_entry_date_s']

    @property
    def holding_stock_avg_price_s(self) -> pd.Series:
        """當前持有的股票平均價 (不考慮手續費)"""
        if 'holding_stock_entry_price_s' not in self._cache:
            stock_entry_price_map = {}
            for position in self.positions:
                if position.stock_id not in stock_entry_price_map:
                    stock_entry_price_map[position.stock_id] = position.avg_price

            self._cache['holding_stock_entry_price_s'] = pd.Series(
                [stock_entry_price_map[stock_id] for stock_id in self.holding_stock_ids],
                index=self.holding_stock_ids,
            )
        return self._cache['holding_stock_entry_price_s']

    @property
    def holding_stock_break_even_price_s(self) -> pd.Series:
        """當前持有的股票入場價 (考慮手續費)"""
        if 'holding_stock_break_even_price_s' not in self._cache:
            fee_ratio = self.commission_info.fee_rate
            tax_ratio = self.commission_info.tax_rate
            self._cache['holding_stock_break_even_price_s'] = self.holding_stock_avg_price_s * (1 + fee_ratio) / (
                    1 - fee_ratio - tax_ratio)
        return self._cache['holding_stock_break_even_price_s']

    @property
    def holding_stock_shares_s(self) -> pd.Series:
        """當前持有的股票股數"""
        if 'holding_stock_shares_s' not in self._cache:
            stock_share_map = {}
            for position in self.positions:
                stock_share_map[position.stock_id] = stock_share_map.get(position.stock_id, 0) + position.shares
            self._cache['holding_stock_shares_s'] = pd.Series(
                [stock_share_map[stock_id] for stock_id in self.holding_stock_ids],
                index=self.holding_stock_ids,
            )
        return self._cache['holding_stock_shares_s']

    @property
    def invested_funds(self) -> int:
        """當前的總投入資金"""
        if 'invested_funds' not in self._cache:
            funds = 0
            for position in self.positions:
                funds += int(position.avg_price * position.shares)
            self._cache['invested_funds'] = funds
        return self._cache['invested_funds']
