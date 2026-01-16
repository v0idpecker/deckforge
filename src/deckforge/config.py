import os

from pydantic import BaseModel, Field


class PostgresConfig(BaseModel):
    url: str = str(os.getenv("POSTGRES_URL"))


class Config(BaseModel):
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
