import abc
import json
import traceback

import asyncio
import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from finance_bot.infrastructure import infra
from finance_bot.model.task_status import TaskStatus


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
                           name,
                           key,
                           func,
                           *,
                           args=None,
                           kargs=None,
                           retries=0):
        if args is None:
            args = []
        if kargs is None:
            kargs = {}

        self.logger.info(f'開始任務 {name} ...')
        for i in range(retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kargs)
                else:
                    result = func(*args, **kargs)
                async with AsyncSession(infra.db.async_engine) as session:
                    await infra.db.insert_or_update(session, TaskStatus, dict(
                        key=key,
                        is_error=False,
                        detail=json.dumps(result),
                    ))
                self.logger.info(f'任務 {name} 成功')
                return
            except:
                async with AsyncSession(infra.db.async_engine) as session:
                    await infra.db.insert_or_update(session, TaskStatus, dict(
                        key=key,
                        is_error=True,
                        detail=traceback.format_exc(),
                    ))

                if retries == 0:
                    self.logger.exception(f'任務 {name} 失敗')
                    return
                else:
                    self.logger.exception(f'任務 {name} 失敗 [重試次數: {i}]')
                    self.logger.info('等待 60 秒 ...')
                    await asyncio.sleep(60)
