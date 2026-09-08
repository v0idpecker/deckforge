import datetime
import logging
from datetime import timedelta

from dishka import Provider, Scope, provide
from dishka.provider import from_context
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from deckforge.config import Config
from deckforge.db.dao.outbox import OutboxEventDAO
from deckforge.services.decks.decktask import DeckTaskService

logger = logging.getLogger(__name__)

class RetryScheduler:
    def __init__(
        self,
        decktask_service: DeckTaskService,
        sessionmaker: async_sessionmaker[AsyncSession],
        outbox_dao: OutboxEventDAO,
        task_timeout_base: int,
        task_timeout_per_item: int,
    ):
        self._decktask_service = decktask_service
        self._sessionmaker = sessionmaker
        self._outbox_dao = outbox_dao
        self._task_timeout_base = task_timeout_base
        self._task_timeout_per_item = task_timeout_per_item

    async def tick(self):
        try:
            rescheduled = await self._decktask_service.reschedule_ready_tasks()
            for task_id in rescheduled:
                logger.info("Task %s was retried", task_id)
        except Exception:
            logger.exception("Failed to reschedule due tasks")

        await self._requeue_stale_tasks()

    async def _requeue_stale_tasks(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        # Ловкий порог: минимально возможный дедлайн (для задач с 1 item),
        # чтобы не выбирать лишние PROCESSING-задачи.
        loose_cutoff = now - timedelta(seconds=self._task_timeout_base)
        try:
            candidates = await self._decktask_service.find_stale_processing_tasks(
                loose_cutoff
            )
        except Exception:
            logger.exception("Failed to fetch stale processing tasks")
            return

        for task in candidates:
            try:
                deadline = self._task_timeout_base + (
                    self._task_timeout_per_item * task.total_items
                )
                if task.updated_at > now - timedelta(seconds=deadline):
                    continue
                logger.warning(
                    "Task %s exceeded processing deadline of %ss, scheduling retry",
                    task.id,
                    deadline,
                )
                await self._decktask_service.mark_for_retry_or_fail(
                    task.id, TimeoutError("task processing timed out")
                )
            except Exception:
                logger.exception("Failed to requeue stale task %s", task.id)

class SchedulerProvider(Provider):
    config = from_context(Config, scope=Scope.APP)

    @provide(scope=Scope.REQUEST)
    async def scheduler(
        self,
        decktask_service: DeckTaskService,
        sessionmaker: async_sessionmaker[AsyncSession],
        outbox_dao: OutboxEventDAO,
        config: Config,
    ) -> RetryScheduler:
        return RetryScheduler(
            decktask_service,
            sessionmaker,
            outbox_dao,
            task_timeout_base=config.asyncio.task_timeout_base,
            task_timeout_per_item=config.asyncio.task_timeout_per_item,
        )
