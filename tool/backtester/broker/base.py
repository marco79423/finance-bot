import abc


class BrokerBase(abc.ABC):

    @property
    @abc.abstractmethod
    def current_balance(self):
        pass
