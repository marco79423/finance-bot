import abc

from finance_bot.infrastructure import infra


class BotBase(abc.ABC):
    name = 'bot_base'

    def __init__(self):
        self.logger = infra.logger.getChild(self.name)
