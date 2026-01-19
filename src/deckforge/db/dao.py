from abc import abstractmethod
from typing import Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from deckforge.db.models.decks import DeckItem, DeckTask
from deckforge.services.dto import DeckItemCreateDTO, DeckTaskCreateDTO


class DAOInterface(Protocol):
    @abstractmethod
    async def list(self):
        raise NotImplementedError

    @abstractmethod
    async def create(self, data):
        raise NotImplementedError


class DeckTaskDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self):
        res = await self.session.execute(select(DeckTask))
        return res.scalars().all()

    async def create(self, data: DeckTaskCreateDTO):
        task = DeckTask(
            status="CREATED",
            current_stage="NONE",
            total_items=len(data.words),
            completed_items=0,
            failed_items=0,
            options=data.options,
        )
        self.session.add(task)

    async def get(self, id: UUID):
        res = await self.session.execute(select(DeckTask).where(DeckTask.id == id))
        return res.scalar()


class DeckItemDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self):
        res = await self.session.execute(select(DeckItem))
        return res.scalars().all()

    async def create(self, data: DeckItemCreateDTO):
        item = DeckItem(
            task_id=data.task_id,
            raw_word=data.raw_word,
            status="PENDING",
            stage="NONE",
        )
        self.session.add(item)

    async def get(self, id: UUID):
        res = await self.session.execute(select(DeckItem).where(DeckItem.id == id))
        return res.scalar()
