import requests
from fake_useragent import UserAgent

from finance_bot.infrastructure.base import ManagerBase


class APIManager(ManagerBase):

    def __init__(self, infra):
        super().__init__(infra)
        self._user_agent = UserAgent()

    def get(self, url, *, params=None):
        return requests.get(
            url=url,
            params=params,
            headers={
                'user-agent': self._user_agent.random
            }
        )

    def post(self, url, **kargs):
        return requests.post(
            url=url,
            **kargs,
            headers={
                'user-agent': self._user_agent.random,
                **kargs.get('headers', {})
            },
        )
