import abc
import dataclasses
import math

import pandas as pd

from finance_bot.infrastructure import infra


@dataclasses.dataclass
class Position:
    id: int
    date: pd.Timestamp
    stock_id: str
    price: float
    shares: int


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
        commission = math.floor(shares * price * self.fee_rate)  # 無條件捨去小數點
        return max(commission, 1)  # 永豐說是最低 1 元

    def get_sell_commission(self, price, shares) -> int:
        commission = math.floor(shares * price * (self.fee_rate + self.tax_rate))  # 無條件捨去小數點
        return max(commission, 1)  # 永豐說是最低 1 元


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

    @property
    @abc.abstractmethod
    def current_balance(self):
        pass

    @property
    @abc.abstractmethod
    def positions(self) -> [Position]:
        pass

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
    def invested_funds(self) -> int:
        """當前的總投入資金"""
        if 'invested_funds' not in self._cache:
            funds = 0
            for position in self.positions:
                funds += int(position.price * position.shares)
            self._cache['invested_funds'] = funds
        return self._cache['invested_funds']
