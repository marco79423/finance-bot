import abc


class BrokerBase(abc.ABC):

    @property
    @abc.abstractmethod
    def current_balance(self):
        pass

    @abc.abstractmethod
    def buy_market(self, stock_id, shares, note=''):
        pass

    @abc.abstractmethod
    def sell_all_market(self, stock_id, note=''):
        pass
