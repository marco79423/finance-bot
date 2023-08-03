import abc
import asyncio

from finance_bot.infrastructure import infra


class ServiceBase(abc.ABC):
    name = 'service_base'

    def __init__(self, app):
        app.state.service[self.name] = self
        self.app = app
        self.logger = infra.logger.getChild(self.name)

    def start(self):
        self.logger.info(f'啟動 {self.name} 功能...')
        self.set_schedules()

    @abc.abstractmethod
    def set_schedules(self):
        pass

    @staticmethod
    async def execute_task(func, *, args=None, kargs=None, success_message=None, error_message=None, retries=0):
        if args is None:
            args = []
        if kargs is None:
            kargs = {}

        for i in range(retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kargs)
                else:
                    result = func(*args, **kargs)

                if success_message:
                    message = success_message.format(
                        *args,
                        **kargs,
                        **(result if isinstance(result, dict) else {})
                    )

                    await infra.notifier.send(message)
                return
            except Exception as e:
                if error_message:
                    message = error_message.format(
                        *args,
                        **kargs,
                        error=str(e),
                        retry_count=i + 1 if retries > 0 else 0
                    )

                    await infra.notifier.send(message)
                await asyncio.sleep(60)
