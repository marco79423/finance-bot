import asyncio

import telegram

from finance_bot.infrastructure.manager.base import ManagerBase


class NotifierManager(ManagerBase):

    def __init__(self, infra):
        super().__init__(infra)
        self._telegram_bot = telegram.Bot(self.conf.infrastructure.notification.telegram.token)

    async def send(self, message: str):
        while True:
            try:
                await self._telegram_bot.send_message(
                    chat_id=self.conf.infrastructure.notification.telegram.chat_id,
                    text=message,
                    connect_timeout=60,
                    pool_timeout=5 * 60,
                )
                return
            except telegram.error.RetryAfter as e:
                await asyncio.sleep(e.retry_after + 1)
                continue