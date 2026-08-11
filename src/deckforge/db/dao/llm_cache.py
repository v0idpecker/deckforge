from typing import List
from uuid import UUID

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select

from deckforge.db.errors import DAOError, DAONotFoundError
from deckforge.db.models.llm_cache import LLMCache
from deckforge.dto.llm_cache import LLMCacheCreateDTO, LLMCacheDTO, LLMCacheKeyDTO


class LLMCacheDAO:
    async def list(self, session: AsyncSession) -> List[LLMCacheDTO]:
        try:
            res = await session.execute(select(LLMCache))
            caches = res.scalars().all()

            return [LLMCacheDTO.from_entity(cache) for cache in caches]
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def create(
        self, session: AsyncSession, data: LLMCacheCreateDTO
    ) -> LLMCacheDTO:
        try:
            stmt = insert(LLMCache).values(**data.__dict__)
            upsert_stmt = stmt.on_conflict_do_update(
                index_elements=[
                    "word",
                    "sentence_lang",
                    "translation_lang",
                    "difficulty",
                    "limit",
                    "model",
                    "prompt_version",
                ],
                set_={"result": stmt.excluded.result},
            ).returning(LLMCache)

            res = await session.execute(upsert_stmt)
            cache = res.scalars().first()
            if cache is None:
                raise DAONotFoundError("Cache not found")

            return LLMCacheDTO.from_entity(cache)
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def get(self, session: AsyncSession, cache_id: UUID) -> LLMCacheDTO:
        try:
            res = await session.execute(select(LLMCache).where(LLMCache.id == cache_id))
            cache = res.scalars().one_or_none()
            if cache is None:
                raise DAONotFoundError("Cache not found")
            return LLMCacheDTO.from_entity(cache)
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def get_by_key(
        self, session: AsyncSession, key: LLMCacheKeyDTO
    ) -> LLMCacheDTO:
        try:
            res = await session.execute(select(LLMCache).filter_by(**key.__dict__))
            cache = res.scalars().one_or_none()
            if cache is None:
                raise DAONotFoundError("Cache not found")
            return LLMCacheDTO.from_entity(cache)
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")
