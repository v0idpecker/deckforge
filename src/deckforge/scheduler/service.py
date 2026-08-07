from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from deckforge.db.dao.outbox import OutboxEventDAO
from deckforge.services.decks.decktask import DeckTaskService


class RetryScheduler:
    def __init__(
        self,
        decktask_service: DeckTaskService,
        sessionmaker: async_sessionmaker[AsyncSession],
        outbox_dao: OutboxEventDAO,
    ):
        self._decktask_service = decktask_service
        self._sessionmaker = sessionmaker
        self._outbox_dao = outbox_dao

    async def tick(self):
        due_tasks = await self._decktask_service.find_ready_for_retry()

        for task in due_tasks:
            await self._decktask_service.reschedule_for_retry(task.id)
            print(f"Task {task.id} was retried!")


class SchedulerProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def scheduler(
        self,
        decktask_service: DeckTaskService,
        sessionmaker: async_sessionmaker[AsyncSession],
        outbox_dao: OutboxEventDAO,
    ) -> RetryScheduler:
        return RetryScheduler(decktask_service, sessionmaker, outbox_dao)
