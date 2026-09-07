import asyncio
import logging
from uuid import UUID

from deckforge.adapters.anki import AnkiAdapter
from deckforge.adapters.errors import ExternalServiceError
from deckforge.adapters.normalizer import Normalizer
from deckforge.dto.deck_card import DeckCardCreateDTO
from deckforge.dto.deck_item import DeckItemDTO
from deckforge.services.contextgen import ContextGenerationService
from deckforge.services.decks.deckcard import DeckCardService
from deckforge.services.decks.deckitem import DeckItemSerivce
from deckforge.services.decks.decktask import DeckTaskService
from deckforge.services.errors import ServiceError

logger = logging.getLogger(__name__)

class DeckPipeline:
    def __init__(
        self,
        decktask_service: DeckTaskService,
        deckitem_service: DeckItemSerivce,
        deckcard_service: DeckCardService,
        normalizer: Normalizer,
        context_generator: ContextGenerationService,
        anki: AnkiAdapter,
        concurrency: int,
    ):
        self._decktask_service = decktask_service
        self._deckitem_service = deckitem_service
        self._deckcard_service = deckcard_service
        self._normalizer = normalizer
        self._context_generator = context_generator
        self._anki = anki
        self._concurrency = concurrency

    async def run(self, task_id: UUID):
        logger.info("Task %s: run started", task_id)
        task = await self._decktask_service.get_task(task_id)
        if task.status in {"DONE", "PARTIALLY_DONE"}:
            logger.info("Task %s skipped, already in final status %s", task_id, task.status)
            return

        claimed = await self._decktask_service.claim_for_processing(task.id)
        if not claimed:
            logger.info("Task %s not claimed, skipping run", task_id)
            return
        logger.info("Task %s claimed for processing", task_id)
        items = await self._deckitem_service.get_task_items(task_id)
        if not items:
            logger.error("No pending deck items found for task %s", task_id)
            raise ServiceError(f"No pending deck items found for task {task_id}")

        logger.info("Task %s: processing %d items", task_id, len(items))

        semaphore = asyncio.Semaphore(self._concurrency)

        async def process_item(item):
            async with semaphore:
                await self.set_in_progress_status(item)
                await self._deckitem_service.update_item(item)

                try:
                    if task.options.get("normalization"):
                        await self.normalize_word(item)
                        await self._deckitem_service.update_item(item)
                    if task.options.get("limit"):
                        cards = await self.get_context_sentence(
                            item,
                            task.options.get("limit", 1),
                            task.options.get("sentence_lang", "english"),
                            task.options.get("translation_lang", "russian"),
                            task.options.get("difficulty", "B1"),
                        )
                        await self._deckcard_service.replace_for_item(item.id, cards)
                        await self._deckitem_service.update_item(item)

                    await self.set_done_status(item)
                    await self._deckitem_service.update_item(item)
                    return None

                except Exception as err:
                    logger.exception(
                        "Task %s: item %s (%s) failed: %s",
                        task_id,
                        item.id,
                        item.raw_word,
                        str(err),
                    )
                    await self._fail_item(item, err)
                    return err

        results = await asyncio.gather(
            *(process_item(item) for item in items), return_exceptions=True
        )
        has_errors = any(r is not None for r in results)

        # Контракт §7.4 №2: ExternalServiceError пробрасывается наружу,
        # чтобы воркер запланировал ретрай задачи.
        external_failures = [r for r in results if isinstance(r, ExternalServiceError)]
        if external_failures:
            logger.error(
                "Task %s: %d item(s) failed with ExternalServiceError, "
                "propagating for retry",
                task_id,
                len(external_failures),
            )
            raise external_failures[0]

        try:
            cards = await self._deckcard_service.list_by_task(task.id)
            if cards:
                self._anki.export_deck(
                    task.id,
                    self._decktask_service.derive_deck_name(task.options),
                    cards,
                )
        except (ServiceError, OSError) as e:
            logger.error(
                "Task %s: export failed, marking for retry: %s", task_id, str(e)
            )
            await self._decktask_service.mark_for_retry_or_fail(task.id, e)
            return

        task_status = "PARTIALLY_DONE" if has_errors else "DONE"
        logger.info("Task %s: completed with status %s", task_id, task_status)
        await self._decktask_service.complete_task(task_id, task_status)

    async def _fail_item(self, item: DeckItemDTO, err: Exception):
        item.status = "ERROR"
        item.error = str(err) or type(err).__name__
        await self._deckitem_service.update_item(item)

    async def set_in_progress_status(self, item: DeckItemDTO):
        if item.status in {"PENDING", "ERROR"}:
            item.status = "PROCESSING"
            item.stage = "INIT"

    async def set_done_status(self, item: DeckItemDTO):
        if item.status == "PROCESSING":
            item.status = "DONE"
            item.stage = "DONE"

    async def normalize_word(self, item: DeckItemDTO):
        normilized_word = self._normalizer.lemmatize_word(item.raw_word)
        item.normalized_word = normilized_word
        item.stage = "NORMILIZED"

    async def get_context_sentence(
        self,
        item: DeckItemDTO,
        limit: int,
        sentence_lang: str,
        translation_lang: str,
        difficulty: str,
    ):
        lookup_word = item.normalized_word or item.raw_word
        examples = await self._context_generator.get_context_sentence(
            lookup_word, limit, sentence_lang, translation_lang, difficulty
        )
        cards = []
        for i, ex in enumerate(examples):
            cards.append(
                DeckCardCreateDTO(
                    task_id=item.task_id,
                    item_id=item.id,
                    word=lookup_word,
                    sentence=ex[sentence_lang],
                    translation=ex[translation_lang],
                    position=i,
                )
            )

        item.stage = "CONTEXT_GENERATED"

        return cards
