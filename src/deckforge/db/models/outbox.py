import datetime
import enum
import uuid

from sqlalchemy.orm import mapped_column
from sqlalchemy.orm.base import Mapped
from sqlalchemy.sql.sqltypes import JSON, TEXT, UUID, DateTime, Enum

from deckforge.db.models.base import Base


class EventStatus(enum.Enum):
    NEW = "new"
    SENT = "sent"


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    event_type: Mapped[str] = mapped_column(TEXT, nullable=False)
    status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus), nullable=False, default=EventStatus.NEW
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.now
    )
