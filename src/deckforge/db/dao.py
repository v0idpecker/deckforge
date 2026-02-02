from abc import abstractmethod
from typing import Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from deckforge.db.models.decks import DeckItem, DeckTask
from deckforge.services.dto import DeckItemCreateDTO, DeckTaskCreateDTO


class DAOInterface(Protocol):
    @abstractmethod
    async def list(self, session):
        raise NotImplementedError

    @abstractmethod
    async def create(self, data, session):
        raise NotImplementedError


class DeckTaskDAO:
    async def list(self, session: AsyncSession):
        res = await session.execute(select(DeckTask))
        return res.scalars().all()

    async def create(self, data: DeckTaskCreateDTO, session: AsyncSession):
        task = DeckTask(
            status="CREATED",
            current_stage="NONE",
            total_items=len(data.words),
            completed_items=0,
            failed_items=0,
            options=data.options,
        )
        session.add(task)
        return task

    async def get(self, id: UUID, session: AsyncSession):
        res = await session.execute(select(DeckTask).where(DeckTask.id == id))
        return res.scalar()


class DeckItemDAO:
    async def list(self, session: AsyncSession):
        res = await session.execute(select(DeckItem))
        return res.scalars().all()

    async def create(self, data: DeckItemCreateDTO, session: AsyncSession):
        item = DeckItem(
            task_id=data.task_id,
            raw_word=data.raw_word,
            status="PENDING",
            stage="NONE",
        )
        session.add(item)
        return item

    async def get(self, id: UUID, session: AsyncSession):
        res = await session.execute(select(DeckItem).where(DeckItem.id == id))
        return res.scalar()
