from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from deckforge.adapters.amqp.queue_publisher import QueuePublisher
from deckforge.db.dao import DeckTaskDAO
from deckforge.services.decks.deckitem import DeckItemSerivce
from deckforge.services.dto import DeckItemCreateDTO, DeckTaskCreateDTO


class DeckTaskService:
    def __init__(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
        deckitem_service: DeckItemSerivce,
        decktask_dao: DeckTaskDAO,
        publisher: QueuePublisher,
    ):
        self._sessionmaker = sessionmaker
        self._deckitem_service = deckitem_service
        self._decktask_dao = decktask_dao
        self._publisher = publisher

    async def create_task(self, dto: DeckTaskCreateDTO):
        async with self._sessionmaker() as session, session.begin():
            task = await self._decktask_dao.create(dto, session)
            await session.flush()
            task_id = task.id

        for word in dto.words:
            item_dto = DeckItemCreateDTO(task_id, word)
            await self._deckitem_service.create_items(item_dto)

        await self._publisher.send(str(task_id))

        return task_id

    async def get_task_status(self, task_id: UUID):
        async with self._sessionmaker() as session, session.begin():
            task = await self._decktask_dao.get(task_id, session)
            return task.status
