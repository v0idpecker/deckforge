import asyncio
import logging

from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from deckforge.adapters.amqp.queue_publisher import QueuePublisher
from deckforge.db.dao.outbox import OutboxEventDAO

logger = logging.getLogger(__name__)

class OutboxRelay:
    def __init__(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
        outbox_event_dao: OutboxEventDAO,
        publisher: QueuePublisher,
        batch_size=10,
    ):
        self._sessionmaker = sessionmaker
        self._outbox_event_dao = outbox_event_dao
        self._publisher = publisher
        self._batch_size = batch_size

    async def run_polling_loop(self, interval=2):
        while True:
            try:
                processed_count = await self.process_batch()

                if processed_count == 0:
                    await asyncio.sleep(interval)
            except Exception:
                logger.exception("Outbox relay iteration failed")
                await asyncio.sleep(interval)

    async def process_batch(self):
        async with self._sessionmaker() as session, session.begin():
            messages = await self._outbox_event_dao.fetch_unsent(
                self._batch_size, session
            )

            if not messages:
                return 0

        for msg in messages:
            await self._publisher.send(msg.payload["task_id"])

        async with self._sessionmaker() as session, session.begin():
            for msg in messages:
                await self._outbox_event_dao.mark_sent(msg.id, session)

        logger.info("Published %d outbox events", len(messages))
        return len(messages)
