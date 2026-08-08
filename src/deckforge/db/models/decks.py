import datetime
import uuid
from typing import List

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import INT, JSON, TEXT, UUID, DateTime

from deckforge.db.models.base import Base
from deckforge.db.models.user import User


class DeckTask(Base):
    __tablename__ = "deck_tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    status: Mapped[str] = mapped_column(TEXT, nullable=False)
    current_stage: Mapped[str] = mapped_column(TEXT)
    total_items: Mapped[int] = mapped_column(INT, nullable=False)
    completed_items: Mapped[int] = mapped_column(INT, default=0)
    failed_items: Mapped[int] = mapped_column(INT, default=0)
    options: Mapped[dict] = mapped_column(JSON, nullable=False)
    error: Mapped[str] = mapped_column(TEXT, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.now
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
    )
    attempt_count: Mapped[int] = mapped_column(INT, nullable=False, default=0)
    next_retry_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    deck_items: Mapped[List["DeckItem"]] = relationship(back_populates="deck_task")
    deck_cards: Mapped[List["DeckCard"]] = relationship(back_populates="deck_task")
    user: Mapped["User"] = relationship(back_populates="tasks")


class DeckItem(Base):
    __tablename__ = "deck_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("deck_tasks.id"))
    raw_word: Mapped[str] = mapped_column(TEXT, nullable=False)
    normalized_word: Mapped[str] = mapped_column(TEXT, nullable=True)
    status: Mapped[str] = mapped_column(TEXT, nullable=False)
    stage: Mapped[str] = mapped_column(TEXT, nullable=False)
    sentence: Mapped[str] = mapped_column(TEXT, nullable=True)
    translation: Mapped[str] = mapped_column(TEXT, nullable=True)
    error: Mapped[str] = mapped_column(TEXT, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.now
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
    )
    deck_task: Mapped["DeckTask"] = relationship(back_populates="deck_items")
    deck_cards: Mapped[List["DeckCard"]] = relationship(back_populates="deck_item")


class DeckCard(Base):
    __tablename__ = "deck_cards"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("deck_tasks.id"))
    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("deck_items.id"))
    word: Mapped[str] = mapped_column(TEXT, nullable=False)
    sentence: Mapped[str] = mapped_column(TEXT, nullable=False)
    translation: Mapped[str] = mapped_column(TEXT, nullable=False)
    position: Mapped[int] = mapped_column(INT, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.now
    )
    deck_task: Mapped["DeckTask"] = relationship(back_populates="deck_cards")
    deck_item: Mapped["DeckItem"] = relationship(back_populates="deck_cards")

    __table_args__ = UniqueConstraint("item_id", "position", name="uix_card_position")
