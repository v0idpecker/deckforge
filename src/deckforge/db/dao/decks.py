from typing import List
from uuid import UUID

from sqlalchemy.exc import (
    DataError,
    IntegrityError,
    MultipleResultsFound,
    SQLAlchemyError,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import and_, select, update

from deckforge.db.errors import (
    DAOError,
    DAOIntegrityError,
    DAOInvalidInputError,
    DAOMultipleResultsError,
    DAONotFoundError,
)
from deckforge.db.models.decks import DeckItem, DeckTask
from deckforge.services.dto import (
    DeckItemCreateDTO,
    DeckItemDTO,
    DeckTaskCreateDTO,
    DeckTaskDTO,
)


class DeckTaskDAO:
    async def list(self, session: AsyncSession) -> List[DeckTaskDTO]:
        try:
            res = await session.execute(select(DeckTask))
            values = res.scalars().all()
            if values == []:
                raise DAONotFoundError("No deck tasks found")
            return [DeckTaskDTO.from_entity(value) for value in values]
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def create(
        self, data: DeckTaskCreateDTO, user_id: UUID, session: AsyncSession
    ) -> DeckTaskDTO:
        try:
            task = DeckTask(
                status="CREATED",
                current_stage="NONE",
                total_items=len(data.words),
                completed_items=0,
                failed_items=0,
                options=data.options,
                user_id=user_id,
            )
            session.add(task)
            await session.flush()
            return DeckTaskDTO.from_entity(task)
        except DataError as e:
            raise DAOInvalidInputError(f"Invalid input data: {e}")
        except IntegrityError as e:
            raise DAOIntegrityError(f"Data integrity error: {e}")
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def get(self, id: UUID, session: AsyncSession) -> DeckTaskDTO:
        try:
            res = await session.execute(select(DeckTask).where(DeckTask.id == id))
            value = res.scalars().one_or_none()
            if value is None:
                raise DAONotFoundError(f"DeckTask with id {id} not found")
            return DeckTaskDTO.from_entity(value)
        except MultipleResultsFound as e:
            raise DAOMultipleResultsError(f"Multiple tasks found with the same id: {e}")
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def update_status(self, session: AsyncSession, id: UUID, status: str) -> None:
        try:
            stmt = (
                update(DeckTask)
                .where(DeckTask.id == id)
                .values(
                    status=status,
                )
            )
            await session.execute(stmt)
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")


class DeckItemDAO:
    async def list(self, session: AsyncSession) -> List[DeckItemDTO]:
        try:
            res = await session.execute(select(DeckItem))
            values = res.scalars().all()
            if values == []:
                raise DAONotFoundError("No deck items found")
            return [DeckItemDTO.from_entity(value) for value in values]
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def create(
        self, data: DeckItemCreateDTO, session: AsyncSession
    ) -> DeckItemDTO:
        try:
            item = DeckItem(
                task_id=data.task_id,
                raw_word=data.raw_word,
                status="PENDING",
                stage="NONE",
            )
            session.add(item)
            return DeckItemDTO.from_entity(item)
        except DataError as e:
            raise DAOInvalidInputError(f"Invalid input data: {e}")
        except IntegrityError as e:
            raise DAOIntegrityError(f"Data integrity error: {e}")
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def get(self, id: UUID, session: AsyncSession) -> DeckItemDTO:
        try:
            res = await session.execute(select(DeckItem).where(DeckItem.id == id))
            value = res.scalars().one_or_none()
            if value is None:
                raise DAONotFoundError(f"DeckItem with id {id} not found")
            return DeckItemDTO.from_entity(value)
        except MultipleResultsFound:
            raise DAOMultipleResultsError(
                f"Multiple DeckItems with the same id {id} found"
            )
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def get_items_by_task_id(
        self, task_id: UUID, session: AsyncSession
    ) -> List[DeckItemDTO]:
        try:
            stmt = select(DeckItem).where(
                and_(DeckItem.task_id == task_id, DeckItem.status == "PENDING")
            )
            res = await session.execute(stmt)
            values = res.scalars().all()
            if values == []:
                raise DAONotFoundError(f"No deck items found for task {task_id}")
            return [DeckItemDTO.from_entity(value) for value in values]
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def set_status(
        self, id: UUID, new_status: str, session: AsyncSession
    ) -> None:
        try:
            res = await session.execute(select(DeckItem).where(DeckItem.id == id))
            value = res.scalars().one_or_none()
            if value is None:
                raise DAONotFoundError(f"DeckItem with id {id} not found")
            value.status = new_status
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def update(self, session: AsyncSession, data: DeckItemDTO) -> None:
        try:
            stmt = (
                update(DeckItem)
                .where(DeckItem.id == data.id)
                .values(
                    status=data.status,
                    normalized_word=data.normalized_word,
                    sentence=data.sentence,
                    translation=data.translation,
                )
            )
            await session.execute(stmt)
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")
