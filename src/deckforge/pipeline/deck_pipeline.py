from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from deckforge.services.decks.deckitem import DeckItemSerivce
from deckforge.services.decks.decktask import DeckTaskService
from deckforge.services.dto import DeckItemDTO


class DeckPipeline:
    def __init__(
        self,
        session: AsyncSession,
        decktask_service: DeckTaskService,
        deckitem_service: DeckItemSerivce,
    ):
        self._session = session
        self._decktask_service = decktask_service
        self._deckitem_service = deckitem_service

    async def run(self, task_id: UUID):
        async with self._session.begin():
            items = await self._deckitem_service.get_task_items(self._session, task_id)
            for item in items:
                await self.set_in_progress_status(item)

    async def set_in_progress_status(self, item: DeckItemDTO):
        await self._deckitem_service.set_status(self._session, item.id, "IN_PROGRESS")
