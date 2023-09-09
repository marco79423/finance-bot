import abc

from finance_bot.infrastructure import infra


class CoreBase(abc.ABC):
    name = 'bot_base'

    def __init__(self):
        self.logger = infra.logger.bind(name=self.name)
