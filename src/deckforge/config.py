import os

from pydantic import BaseModel, Field


class PostgresConfig(BaseModel):
    url: str = Field(default_factory=lambda: str(os.getenv("POSTGRES_URL")))


class RabbitMQConfig(BaseModel):
    url: str = Field(default_factory=lambda: str(os.getenv("RABBITMQ_URL")))
    queue_name: str = "pipeline_queue"


class OAuth2Config(BaseModel):
    google_client_id: str = Field(
        default_factory=lambda: str(os.getenv("GOOGLE_CLIENT_ID"))
    )
    google_client_secret: str = Field(
        default_factory=lambda: str(os.getenv("GOOGLE_CLIENT_SECRET"))
    )
    jwt_secret: str = Field(default_factory=lambda: str(os.getenv("JWT_SECRET")))


class Config(BaseModel):
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    rabbitmq: RabbitMQConfig = Field(default_factory=RabbitMQConfig)
    oauth2: OAuth2Config = Field(default_factory=OAuth2Config)


def create_config():
    return Config()
