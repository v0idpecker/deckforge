from abc import abstractmethod
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select



class DAOInterface(Protocol):
    @abstractmethod
    async def list(self):
        raise NotImplementedError

    @abstractmethod
    async def create(self, data):
        raise NotImplementedError
