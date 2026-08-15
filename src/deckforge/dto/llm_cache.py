from dataclasses import dataclass
from uuid import UUID

from deckforge.db.models.llm_cache import LLMCache


@dataclass
class LLMCacheDTO:
    id: UUID
    word: str
    sentence_lang: str
    translation_lang: str
    difficulty: str
    limit: int
    model: str
    prompt_version: int
    result: list[dict]

    @classmethod
    def from_entity(cls, entity: LLMCache):
        return cls(
            id=entity.id,
            word=entity.word,
            sentence_lang=entity.sentence_lang,
            translation_lang=entity.translation_lang,
            difficulty=entity.difficulty,
            limit=entity.limit,
            model=entity.model,
            prompt_version=entity.prompt_version,
            result=entity.result,
        )


@dataclass
class LLMCacheCreateDTO:
    word: str
    sentence_lang: str
    translation_lang: str
    difficulty: str
    limit: int
    model: str
    prompt_version: int
    result: list[dict]


@dataclass
class LLMCacheKeyDTO:
    word: str
    sentence_lang: str
    translation_lang: str
    difficulty: str
    limit: int
    model: str
    prompt_version: int
