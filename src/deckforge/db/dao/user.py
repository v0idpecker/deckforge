import uuid
from typing import List

from sqlalchemy.exc import DataError, IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import select

from deckforge.db.errors import (
    DAOError,
    DAOIntegrityError,
    DAOInvalidInputError,
    DAONotFoundError,
)
from deckforge.db.models.user import User
from deckforge.services.dto import UserDTO


class UserDAO:
    async def list(self, session: AsyncSession) -> List[UserDTO]:
        try:
            res = await session.execute(select(User))
            values = res.scalars().all()
            if not values:
                raise DAONotFoundError("No users found")
            return [UserDTO.from_entity(value) for value in values]
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def create(self, session: AsyncSession, data: UserDTO) -> UserDTO:
        try:
            user = User(
                email=data.email,
                name=data.name,
                google_id=data.google_id,
            )
            session.add(user)
            await session.flush()
            return UserDTO.from_entity(user)
        except DataError as e:
            raise DAOInvalidInputError(f"Invalid input data: {e}")
        except IntegrityError as e:
            raise DAOIntegrityError(f"Data integrity error: {e}")
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def get(self, session: AsyncSession, user_id: uuid.UUID) -> UserDTO:
        try:
            res = await session.execute(select(User).where(User.id == user_id))
            value = res.scalar()
            if not value:
                raise DAONotFoundError(f"User not found: {user_id}")
            return UserDTO.from_entity(value)
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")
