import datetime as dt
import time

import requests
from fake_useragent import UserAgent

from finance_bot.infrastructure.base import ManagerBase


class APIManager(ManagerBase):

    def __init__(self, infra):
        super().__init__(infra)
        self._user_agent = UserAgent()
        self._next_avail_request_time = dt.datetime.now()

    def get(self, url, *, params=None, cooling_time=None):
        if dt.datetime.now() < self._next_avail_request_time:
            wait_seconds = int((self._next_avail_request_time - dt.datetime.now()).total_seconds())
            self.logger.info(f'請求冷卻 {wait_seconds} 秒 ...')
            time.sleep(wait_seconds)
        try:
            return requests.get(
                url=url,
                params=params,
                headers={
                    'user-agent': self._user_agent.random
                }
            )
        finally:
            if cooling_time:
                self._next_avail_request_time = dt.datetime.now() + cooling_time

    def post(self, url, cooling_time=None, **kargs):
        if dt.datetime.now() > self._next_avail_request_time:
            wait_seconds = (dt.datetime.now() - self._next_avail_request_time).total_seconds()
            self.logger.info(f'請求冷卻 {wait_seconds} 秒 ...')
            time.sleep(wait_seconds)

        try:
            return requests.post(
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
