import abc


class ManagerBase(abc.ABC):
    def __init__(self, infra):
        self.infra = infra

    def start(self):
        pass

    @property
    def logger(self):
        return self.infra.logger.bind(name='infra')

    @property
    def conf(self):
        return self.infra.conf
