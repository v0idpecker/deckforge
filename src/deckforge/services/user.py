from sqlalchemy.ext.asyncio.session import async_sessionmaker

from deckforge.db.dao.user import UserDAO
from deckforge.db.errors import (
    DAOError,
    DAOIntegrityError,
    DAOInvalidInputError,
    DAONotFoundError,
)
from deckforge.dto.user import UserCreateDTO, UserDTO
from deckforge.services.errors import (
    ConflictError,
    InvalidInputError,
    NotFoundError,
    ServiceError,
)


class UserService:
    def __init__(self, sessionmaker: async_sessionmaker, dao: UserDAO):
        self._user_dao = dao
        self._sessionmaker = sessionmaker

    async def get_or_create(self, data: UserCreateDTO) -> UserDTO:
        async with self._sessionmaker() as session, session.begin():
            try:
                return await self._user_dao.get_by_google_id(session, data.google_id)
            except DAONotFoundError:
                return await self._user_dao.create(session, data)
            except DAOInvalidInputError as e:
                raise InvalidInputError(str(e)) from e
            except DAOIntegrityError as e:
                raise ConflictError(str(e)) from e
            except DAOError as e:
                raise ServiceError(str(e)) from e

    async def get_by_id(self, user_id: str) -> UserDTO:
        async with self._sessionmaker() as session, session.begin():
            try:
                return await self._user_dao.get_by_id(session, user_id)
            except DAONotFoundError:
                raise NotFoundError(f"User not found: {user_id}")
            except DAOError as e:
                raise ServiceError(str(e)) from e
