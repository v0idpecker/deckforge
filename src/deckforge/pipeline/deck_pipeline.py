from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from deckforge.services.decks.deckitem import DeckItemSerivce
from deckforge.services.decks.decktask import DeckTaskService


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
        print("ugabuga")

    async def set_in_progress_status(self, items: List):
        pass
