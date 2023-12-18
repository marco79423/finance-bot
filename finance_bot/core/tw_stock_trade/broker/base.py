import abc
import dataclasses

import pandas as pd

from finance_bot.infrastructure import infra


@dataclasses.dataclass
class Position:
    id: int
    date: pd.Timestamp
    stock_id: str
    price: float
    shares: int


class BrokerBase(abc.ABC):
    name = 'broker_base'

    def __init__(self):
        self.logger = infra.logger.bind(name=self.name)

    @property
    @abc.abstractmethod
    def current_balance(self):
        pass

    @property
    @abc.abstractmethod
    def positions(self) -> [Position]:
        pass

    @abc.abstractmethod
    def buy_market(self, stock_id, shares, note=''):
        """發現沒錢就自動放棄購買"""
        pass

    @abc.abstractmethod
    def sell_all_market(self, stock_id, note=''):
        pass
