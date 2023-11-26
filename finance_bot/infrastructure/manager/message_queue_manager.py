import json

import nats

from finance_bot.infrastructure.manager.base import ManagerBase


class MessageQueueManager(ManagerBase):

    def __init__(self, infra):
        super().__init__(infra)
        self.nc = None

    async def publish(self, subject, data):
        if not self.nc:
            self.nc = await nats.connect(self.conf.infrastructure.message_queue.url)
        await self.nc.publish(subject=subject, payload=json.dumps(data).encode())

    async def subscribe(self, subject, handler, **kargs):
        if not self.nc:
            self.nc = await nats.connect(self.conf.infrastructure.message_queue.url)

        async def wrapped_handler(msg):
            data = json.loads(msg.data)
            await handler(subject, data)

        await self.nc.subscribe(subject=subject, cb=wrapped_handler, **kargs)
