import uuid
from typing import List

from sqlalchemy.exc import DataError, IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import select, update

from deckforge.db.errors import (
    DAOError,
    DAOIntegrityError,
    DAOInvalidInputError,
)
from deckforge.db.models.outbox import EventStatus, OutboxEvent
from deckforge.dto.outbox_event import OutboxEventCreateDTO, OutboxEventDTO

class OutboxEventDAO:
    async def list(self, session: AsyncSession) -> List[OutboxEventDTO]:
        try:
            res = await session.execute(select(OutboxEvent))
            values = res.scalars().all()
            return [OutboxEventDTO.from_entity(value) for value in values]
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def create(
        self, event: OutboxEventCreateDTO, session: AsyncSession
    ) -> OutboxEventDTO:
        try:
            outbox_event = OutboxEvent(
                payload=event.payload,
                event_type=event.event_type,
            )
            session.add(outbox_event)
            await session.flush()
            return OutboxEventDTO.from_entity(outbox_event)
        except DataError as e:
            raise DAOInvalidInputError(f"Invalid input data: {e}")
        except IntegrityError as e:
            raise DAOIntegrityError(f"Data integrity error: {e}")
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def mark_sent(self, id: uuid.UUID, session: AsyncSession):
        try:
            stmt = (
                update(OutboxEvent)
                .where(OutboxEvent.id == id, OutboxEvent.status == EventStatus.NEW)
                .values(status=EventStatus.SENT)
                .returning(OutboxEvent.id)
            )
            res = await session.execute(stmt)
            return res.scalar_one_or_none() is not None
        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")

    async def fetch_unsent(
        self, limit: int, session: AsyncSession
    ) -> List[OutboxEventDTO]:
        try:
            stmt = (
                select(OutboxEvent)
                .where(OutboxEvent.status == EventStatus.NEW)
                .order_by(OutboxEvent.created_at)
                .limit(limit)
                .with_for_update(skip_locked=True)
            )
            res = await session.execute(stmt)
            values = res.scalars().all()

            return [OutboxEventDTO.from_entity(value) for value in values]

        except SQLAlchemyError as e:
            raise DAOError(f"Unexpected database error: {e}")
