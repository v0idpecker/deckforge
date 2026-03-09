from uuid import UUID

from deckforge.adapters.anki import AnkiAdapter
from deckforge.adapters.context_generator import ContextGenerator
from deckforge.adapters.errors import ExternalServiceError
from deckforge.adapters.normalizer import Normalizer
from deckforge.services.decks.deckitem import DeckItemSerivce
from deckforge.services.decks.decktask import DeckTaskService
from deckforge.services.dto import DeckItemDTO


class DeckPipeline:
    def __init__(
        self,
        decktask_service: DeckTaskService,
        deckitem_service: DeckItemSerivce,
        normalizer: Normalizer,
        context_generator: ContextGenerator,
        anki: AnkiAdapter,
    ):
        self._decktask_service = decktask_service
        self._deckitem_service = deckitem_service
        self._normalizer = normalizer
        self._context_generator = context_generator
        self._anki = anki

    async def run(self, task_id: UUID):
        await self._decktask_service.update_task_status(task_id, "PROCESSING")
        # partially done
        items = await self._deckitem_service.get_task_items(task_id)
        has_errors = False
        for item in items:
            await self.set_in_progress_status(item)
            await self._deckitem_service.update_item(item)

            try:
                await self.normalize_word(item)
                await self._deckitem_service.update_item(item)

                await self.get_context_sentence(item)
                await self._deckitem_service.update_item(item)

            except ExternalServiceError:
                await self.set_error_status(item)
                await self._deckitem_service.update_item(item)
                has_errors = True
                continue

            await self.set_done_status(item)
            await self._deckitem_service.update_item(item)

            print(item.__dict__)

        task_status = "PARTIALLY_DONE" if has_errors else "DONE"
        await self._decktask_service.update_task_status(task_id, task_status)

    async def set_in_progress_status(self, item: DeckItemDTO):
        if item.status == "PENDING":
            item.status = "PROCESSING"
            item.stage = "INIT"

    async def set_done_status(self, item: DeckItemDTO):
        if item.status == "PROCESSING":
            item.status = "DONE"
            item.stage = "DONE"

    async def set_error_status(self, item: DeckItemDTO):
        if item.status == "PROCESSING":
            item.status = "ERROR"

    async def normalize_word(self, item: DeckItemDTO):
        normilized_word = self._normalizer.lemmatize_word(item.raw_word)
        item.normalized_word = normilized_word
        item.stage = "NORMILIZED"

    async def get_context_sentence(self, item: DeckItemDTO):
        examples = self._context_generator.get_context_sentence(item.normalized_word, 1)
        for ex in examples:
            item.sentence = ex["english"]
            item.translation = ex["russian"]

        item.stage = "CONTEXT_GENERATED"
