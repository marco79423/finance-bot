import abc

from finance_bot.infrastructure import infra


class BrokerBase(abc.ABC):

    def __init__(self):
        self.logger = infra.logger.bind(name=self.name)

    @property
    @abc.abstractmethod
    def current_balance(self):
        pass

    @property
    @abc.abstractmethod
    def current_holding(self):
        pass

    @abc.abstractmethod
    def buy_market(self, stock_id, shares, note=''):
        """發現沒錢就自動放棄購買"""
        pass

    @abc.abstractmethod
    def sell_all_market(self, stock_id, note=''):
        pass
