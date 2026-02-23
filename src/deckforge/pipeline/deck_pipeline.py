from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from deckforge.adapters.anki import AnkiAdapter
from deckforge.adapters.context_generator import ContextGenerator
from deckforge.adapters.normalizer import Normilizer
from deckforge.services.decks.deckitem import DeckItemSerivce
from deckforge.services.decks.decktask import DeckTaskService
from deckforge.services.dto import DeckItemDTO


class DeckPipeline:
    def __init__(
        self,
        session: AsyncSession,
        decktask_service: DeckTaskService,
        deckitem_service: DeckItemSerivce,
        normalizer: Normilizer,
        context_generator: ContextGenerator,
        anki: AnkiAdapter,
    ):
        self._session = session
        self._decktask_service = decktask_service
        self._deckitem_service = deckitem_service
        self._normalizer = normalizer
        self._context_generator = context_generator
        self._anki = anki

    async def run(self, task_id: UUID):
        async with self._session.begin():
            items = await self._deckitem_service.get_task_items(self._session, task_id)
            for item in items:
                await self.set_in_progress_status(item)
                await self.normilize_word(item)
                await self.get_context_sentence(item)
                await self.set_done_status(item)
                await self.update_item(item)
                print(item.__dict__)

    async def set_in_progress_status(self, item: DeckItemDTO):
        if item.status == "PENDING":
            item.status = "PROCESSING"

    async def set_done_status(self, item: DeckItemDTO):
        if item.status == "PROCESSING":
            item.status = "DONE"

    async def normilize_word(self, item: DeckItemDTO):
        normilized_word = self._normalizer.lemmatize_word(item.raw_word)
        item.normalized_word = normilized_word

    async def get_context_sentence(self, item: DeckItemDTO):
        examples = self._context_generator.get_context_sentence(item.normalized_word, 1)
        for ex in examples:
            item.sentence = ex["english"]
            item.translation = ex["russian"]

    async def update_item(self, item: DeckItemDTO):
        await self._deckitem_service.update_item(self._session, item)
