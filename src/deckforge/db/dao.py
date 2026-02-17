from abc import abstractmethod
from typing import List, Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import and_, select, update

from deckforge.db.models.decks import DeckItem, DeckTask
from deckforge.services.dto import (
    DeckItemCreateDTO,
    DeckItemDTO,
    DeckTaskCreateDTO,
    DeckTaskDTO,
)


class DAOInterface(Protocol):
    @abstractmethod
    async def list(self, session):
        raise NotImplementedError

    @abstractmethod
    async def create(self, data, session):
        raise NotImplementedError


class DeckTaskDAO:
    async def list(self, session: AsyncSession) -> List[DeckTaskDTO]:
        res = await session.execute(select(DeckTask))
        values = res.scalars().all()
        return [DeckTaskDTO.from_entity(value) for value in values]

    async def create(
        self, data: DeckTaskCreateDTO, session: AsyncSession
    ) -> DeckTaskDTO:
        task = DeckTask(
            status="CREATED",
            current_stage="NONE",
            total_items=len(data.words),
            completed_items=0,
            failed_items=0,
            options=data.options,
        )
        session.add(task)
        await session.flush()
        return DeckTaskDTO.from_entity(task)

    async def get(self, id: UUID, session: AsyncSession) -> DeckTaskDTO:
        res = await session.execute(select(DeckTask).where(DeckTask.id == id))
        value = res.scalars().one()
        return DeckTaskDTO.from_entity(value)


class DeckItemDAO:
    async def list(self, session: AsyncSession) -> List[DeckItemDTO]:
        res = await session.execute(select(DeckItem))
        values = res.scalars().all()
        return [DeckItemDTO.from_entity(value) for value in values]

    async def create(
        self, data: DeckItemCreateDTO, session: AsyncSession
    ) -> DeckItemDTO:
        item = DeckItem(
            task_id=data.task_id,
            raw_word=data.raw_word,
            status="PENDING",
            stage="NONE",
        )
        session.add(item)
        return DeckItemDTO.from_entity(item)

    async def get(self, id: UUID, session: AsyncSession) -> DeckItemDTO:
        res = await session.execute(select(DeckItem).where(DeckItem.id == id))
        value = res.scalars().one()
        return DeckItemDTO.from_entity(value)

    async def get_items_by_task_id(
        self, task_id: UUID, session: AsyncSession
    ) -> List[DeckItemDTO]:
        stmt = select(DeckItem).where(
            and_(DeckItem.task_id == task_id, DeckItem.status == "PENDING")
        )
        res = await session.execute(stmt)
        values = res.scalars().all()
        return [DeckItemDTO.from_entity(value) for value in values]

    async def set_status(
        self, id: UUID, new_status: str, session: AsyncSession
    ) -> None:
        res = await session.execute(select(DeckItem).where(DeckItem.id == id))
        item = res.scalars().one()
        if item:
            item.status = new_status

    async def update_item(self, session: AsyncSession, data: DeckItemDTO) -> None:
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
