import asyncio
import datetime as dt

import httpx
from fake_useragent import UserAgent

from finance_bot.infrastructure.base import ManagerBase


class APIManager(ManagerBase):

    def __init__(self, infra):
        super().__init__(infra)
        self._user_agent = UserAgent()
        self._next_avail_request_time = dt.datetime.now()

    async def get(self, url, *, params=None, cooling_time=None):
        if dt.datetime.now() < self._next_avail_request_time:
            wait_seconds = int((self._next_avail_request_time - dt.datetime.now()).total_seconds())
            self.logger.info(f'請求冷卻 {wait_seconds} 秒 ...')
            await asyncio.sleep(wait_seconds)
        try:
            async with httpx.AsyncClient() as client:
                return await client.get(
                    url=url, params=params,
                    headers={
                        'user-agent': self._user_agent.random
                    }
                )
        finally:
            if cooling_time:
                self._next_avail_request_time = dt.datetime.now() + cooling_time

    async def post(self, url, cooling_time=None, **kargs):
        if dt.datetime.now() < self._next_avail_request_time:
            wait_seconds = int((self._next_avail_request_time - dt.datetime.now()).total_seconds())
            self.logger.info(f'請求冷卻 {wait_seconds} 秒 ...')
            await asyncio.sleep(wait_seconds)

        try:
            async with httpx.AsyncClient() as client:
                return await client.post(
                    url=url,
                    **kargs,
                    headers={
                        'user-agent': self._user_agent.random,
                        **kargs.get('headers', {})
                    },
                )
        finally:
            if cooling_time:
                self._next_avail_request_time = dt.datetime.now() + cooling_time
