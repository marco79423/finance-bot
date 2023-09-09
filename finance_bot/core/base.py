import abc

from finance_bot.infrastructure import infra


class CoreBase(abc.ABC):
    name = 'core_base'

    def __init__(self):
        self.logger = infra.logger.bind(name=self.name)
