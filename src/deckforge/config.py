import os

from pydantic import BaseModel, Field


class PostgresConfig(BaseModel):
    url: str = Field(default_factory=lambda: str(os.getenv("POSTGRES_URL")))


class RabbitMQConfig(BaseModel):
    url: str = Field(default_factory=lambda: str(os.getenv("RABBITMQ_URL")))


class Config(BaseModel):
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    rabbitmq: RabbitMQConfig = Field(default_factory=RabbitMQConfig)


def create_config():
    return Config()
