import abc


class BrokerBase(abc.ABC):

    @property
    @abc.abstractmethod
    def current_balance(self):
        pass

    @abc.abstractmethod
    def buy_market(self, stock_id, shares, note=''):
        """發現沒錢就自動放棄購買"""
        pass

    @abc.abstractmethod
    def sell_all_market(self, stock_id, note=''):
        pass
