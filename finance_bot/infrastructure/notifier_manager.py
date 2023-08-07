import telegram

from finance_bot.infrastructure.base import ManagerBase


class NotifierManager(ManagerBase):

    def __init__(self, infra):
        super().__init__(infra)
        self._telegram_bot = telegram.Bot(self.conf.notification.telegram.token)

    async def send(self, message: str):
        await self._telegram_bot.send_message(
            chat_id=self.conf.notification.telegram.chat_id,
            text=message,
            connect_timeout=60,
            pool_timeout=5 * 60,
        )
