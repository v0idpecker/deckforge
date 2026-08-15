from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from deckforge.adapters.context_generator import PROMPT_VERSION, ContextGenerator
from deckforge.dto.llm_cache import LLMCacheCreateDTO, LLMCacheKeyDTO
from deckforge.services.llm_cache import LLMCacheService


class ContextGenerationService:
    def __init__(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
        generator: ContextGenerator,
        cache_service: LLMCacheService,
    ):
        self._sessionmaker = sessionmaker
        self._generator = generator
        self._cache_service = cache_service

    async def get_context_sentence(
        self,
        word: str,
        limit: int,
        sentence_lang: str,
        translation_lang: str,
        difficulty: str,
    ) -> list[dict]:
        key = LLMCacheKeyDTO(
            word=word,
            limit=limit,
            sentence_lang=sentence_lang,
            translation_lang=translation_lang,
            difficulty=difficulty,
            prompt_version=PROMPT_VERSION,
            model=self._generator.model,
        )
        cache = await self._cache_service.get_by_key(key)
        if cache:
            return cache.result
        res = await self._generator.get_context_sentence(
            word=word,
            limit=limit,
            sentence_lang=sentence_lang,
            translation_lang=translation_lang,
            difficulty=difficulty,
        )
        create_dto = LLMCacheCreateDTO(
            word=word,
            sentence_lang=sentence_lang,
            translation_lang=translation_lang,
            limit=limit,
            difficulty=difficulty,
            prompt_version=PROMPT_VERSION,
            model=self._generator.model,
            result=res,
        )
        await self._cache_service.create(create_dto)

        return res
