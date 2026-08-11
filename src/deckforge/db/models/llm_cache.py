import datetime
import uuid

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import INT, JSON, TEXT, UUID, DateTime

from deckforge.db.models.base import Base


class LLMCache(Base):
    __tablename__ = "llm_cache"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    word: Mapped[str] = mapped_column(TEXT, nullable=False)
    sentence_lang: Mapped[str] = mapped_column(TEXT, nullable=False)
    translation_lang: Mapped[str] = mapped_column(TEXT, nullable=False)
    difficulty: Mapped[str] = mapped_column(TEXT, nullable=False)
    limit: Mapped[int] = mapped_column(INT, nullable=False)
    model: Mapped[str] = mapped_column(TEXT, nullable=False)
    prompt_version: Mapped[int] = mapped_column(INT, nullable=False)
    result: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "word",
            "sentence_lang",
            "translation_lang",
            "difficulty",
            "limit",
            "model",
            "prompt_version",
        ),
    )
