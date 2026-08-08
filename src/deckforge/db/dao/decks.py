import datetime
from typing import List
from uuid import UUID

from sqlalchemy import delete
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
from deckforge.db.models.decks import DeckCard, DeckItem, DeckTask
from deckforge.dto.deck_card import DeckCardCreateDTO, DeckCardDTO
from deckforge.dto.deck_item import DeckItemCreateDTO, DeckItemDTO
from deckforge.dto.deck_task import DeckTaskCreateDTO, DeckTaskDTO


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
                status="PENDING",
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

    async def get_by_user(
        self, user_id: UUID, session: AsyncSession
    ) -> List[DeckTaskDTO]:
        try:
            res = await session.execute(
                select(DeckTask).where(DeckTask.user_id == user_id)
            )
            values = res.scalars().all()
            return [DeckTaskDTO.from_entity(value) for value in values]
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def claim_for_processing(self, task_id: UUID, session: AsyncSession) -> bool:
        try:
            stmt = (
                update(DeckTask)
                .where(DeckTask.id == task_id, DeckTask.status == "PENDING")
                .values(status="PROCESSING")
                .returning(DeckTask.id)
            )
            res = await session.execute(stmt)
            claimed_task_id = res.scalar_one_or_none()

            return claimed_task_id is not None
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def update(self, new_task: DeckTaskDTO, session: AsyncSession):
        try:
            stmt = (
                update(DeckTask)
                .where(DeckTask.id == new_task.id)
                .values(**new_task.__dict__)
            )
            await session.execute(stmt)
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def get_tasks_ready_for_retry(
        self, session: AsyncSession, next_retry_at: datetime.datetime
    ) -> List[DeckTaskDTO]:
        try:
            stmt = select(DeckTask).where(
                DeckTask.status == "RETRY_SCHEDULED",
                DeckTask.next_retry_at <= next_retry_at,
            )
            res = await session.execute(stmt)
            tasks = res.scalars().all()

            return [DeckTaskDTO.from_entity(task) for task in tasks]
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def complete(self, session: AsyncSession, id: UUID, status: str) -> None:
        try:
            stmt = (
                update(DeckTask)
                .where(DeckTask.id == id)
                .values(
                    status=status,
                    attempt_count=0,
                    next_retry_at=None,
                    error=None,
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
                and_(
                    DeckItem.task_id == task_id,
                    DeckItem.status.in_(("PENDING", "PROCESSING", "ERROR")),
                )
            )
            res = await session.execute(stmt)
            values = res.scalars().all()
            return [DeckItemDTO.from_entity(value) for value in values]
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def get_all_items_by_task_id(
        self, task_id: UUID, session: AsyncSession
    ) -> List[DeckItemDTO]:
        try:
            res = await session.execute(
                select(DeckItem).where(DeckItem.task_id == task_id)
            )
            values = res.scalars().all()
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
                    stage=data.stage,
                    normalized_word=data.normalized_word,
                    sentence=data.sentence,
                    translation=data.translation,
                )
            )
            await session.execute(stmt)
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")


class DeckCardDAO:
    async def list(self, session: AsyncSession) -> List[DeckCardDTO]:
        try:
            res = await session.execute(select(DeckCard))
            values = res.scalars().all()
            return [DeckCardDTO.from_entity(value) for value in values]
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def create(
        self, data: DeckCardCreateDTO, session: AsyncSession
    ) -> DeckCardDTO:
        try:
            card = DeckCard(
                task_id=data.task_id,
                item_id=data.item_id,
                word=data.word,
                sentence=data.sentence,
                translation=data.translation,
                position=data.position,
            )
            session.add(card)
            return DeckCardDTO.from_entity(card)
        except DataError as e:
            raise DAOInvalidInputError(f"Invalid input data: {e}")
        except IntegrityError as e:
            raise DAOIntegrityError(f"Data integrity error: {e}")
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def list_by_task(
        self, session: AsyncSession, task_id: UUID
    ) -> List[DeckCardDTO]:
        try:
            stmt = (
                select(DeckCard)
                .where(DeckCard.task_id == task_id)
                .order_by(DeckCard.created_at)
            )
            res = await session.execute(stmt)
            cards = res.scalars().all()

            return [DeckCardDTO.from_entity(card) for card in cards]
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def replace_for_item(
        self, session: AsyncSession, item_id: UUID, cards: List[DeckCardDTO]
    ):
        try:
            delete_stmt = delete(DeckCard).where(DeckCard.item_id == item_id)
            await session.execute(delete_stmt)

            new_cards = [
                DeckCard(
                    task_id=card.task_id,
                    item_id=item_id,
                    word=card.word,
                    sentence=card.sentence,
                    translation=card.translation,
                    position=i,
                )
                for i, card in enumerate(cards)
            ]
            session.add_all(new_cards)
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")
