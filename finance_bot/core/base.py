import abc

import asyncio

import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from finance_bot.infrastructure import infra


class CoreBase(abc.ABC):
    name = 'core_base'

    def __init__(self):
        self.logger = infra.logger.bind(name=self.name)

    def get_app(self):
        app = fastapi.FastAPI()

        # 設定第三方擴充
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # 設定預設路由
        app.mount('/data', StaticFiles(directory=infra.path.data_folder), name="data")

        return app

    async def execute_task(self,
                           func,
                           *,
                           args=None,
                           kargs=None,
                           success_message=None,
                           error_message=None,
                           retries=0):
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
                message = ''
                if error_message is not None:
                    message = error_message.format(
                        *args,
                        **kargs,
                        retry_count=i + 1 if retries > 0 else 0
                    )
                self.logger.exception(message)

                if message:
                    message += '\n' + str(e)
                    await infra.notifier.send(message)

                await asyncio.sleep(60)
