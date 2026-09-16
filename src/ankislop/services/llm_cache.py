from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ankislop.db.dao.llm_cache import LLMCacheDAO
from ankislop.db.errors import DAOError
from ankislop.dto.llm_cache import LLMCacheCreateDTO, LLMCacheDTO, LLMCacheKeyDTO
from ankislop.services.errors import ServiceError


class LLMCacheService:
    def __init__(
        self, sessionmaker: async_sessionmaker[AsyncSession], dao: LLMCacheDAO
    ):
        self._sessionmaker = sessionmaker
        self._dao = dao

    async def create(self, cache: LLMCacheCreateDTO) -> LLMCacheDTO:
        try:
            async with self._sessionmaker() as session, session.begin():
                return await self._dao.create(session, cache)
        except DAOError as e:
            raise ServiceError(str(e)) from e

    async def get_by_key(self, key: LLMCacheKeyDTO) -> LLMCacheDTO | None:
        try:
            async with self._sessionmaker() as session, session.begin():
                return await self._dao.get_by_key(session, key)
        except DAOError as e:
            raise ServiceError(str(e)) from e
