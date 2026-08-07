import uuid
from dataclasses import dataclass

from deckforge.db.models.user import User


@dataclass
class UserDTO:
    id: uuid.UUID
    name: str | None
    email: str
    google_id: str | None

    @classmethod
    def from_entity(cls, entity: User) -> "UserDTO":
        return cls(
            id=entity.id,
            name=entity.name,
            email=entity.email,
            google_id=entity.google_id,
        )


@dataclass
class UserCreateDTO:
    name: str | None
    email: str | None
    google_id: str | None
