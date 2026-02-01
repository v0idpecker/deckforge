from typing import Protocol

from faststream.rabbit import RabbitBroker


class QueuePublisher(Protocol):
    async def send(self, msg: str):
        raise NotImplementedError


class RabbitPublisher:
    def __init__(self, broker: RabbitBroker, queue_name: str):
        self._broker = broker
        self._queue = queue_name

    async def send(self, msg: str):
        async with self._broker as broker:
            await broker.publish(msg, self._queue)
