import abc
import asyncio

import telegram

from finance_bot.config import conf


class ServiceBase:
    name = 'service_base'

    def __init__(self, app):
        app.state.service[self.name] = self
        self.app = app
        self.logger = app.state.logger.getChild(self.name)
        self.telegram_bot = telegram.Bot(conf.notification.telegram.token)

    def start(self):
        self.logger.info(f'啟動 {self.name} 功能...')
        self.set_schedules()

    @abc.abstractmethod
    def set_schedules(self):
        pass

    @property
    def config(self):
        return self.app.state.config

    @property
    def scheduler(self):
        return self.app.state.scheduler

    async def execute_task(self, func, *, args=None, kargs=None, success_message=None, error_message=None, retries=0):
        if args is None:
            args = []
        if kargs is None:
            kargs = {}

        for i in range(retries+1):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kargs)
                else:
                    result = func(*args, **kargs)

                if success_message:
                    message = success_message.format(*args, **kargs)
                    if isinstance(result, dict):
                        message = message.format(**result)

                    await self.telegram_bot.send_message(
                        chat_id=conf.notification.telegram.chat_id,
                        text=message
                    )
                return
            except Exception as e:
                if error_message:
                    message = error_message.format(*args, **kargs, error=str(e))
                    if retries > 0:
                        message.format(retry_count=i+1)

                    await self.telegram_bot.send_message(
                        chat_id=conf.notification.telegram.chat_id,
                        text=message
                    )
                await asyncio.sleep(60)
