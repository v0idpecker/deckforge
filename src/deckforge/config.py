import os

from pydantic import BaseModel, Field


def _csv_env(name: str, default: str) -> list[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


class PostgresConfig(BaseModel):
    url: str = Field(default_factory=lambda: str(os.getenv("POSTGRES_URL")))


class RabbitMQConfig(BaseModel):
    url: str = Field(default_factory=lambda: str(os.getenv("RABBITMQ_URL")))
    queue_name: str = "pipeline_queue"


class LLMConfig(BaseModel):
    api_key: str = Field(default_factory=lambda: str(os.getenv("LLM_API_KEY")))
    base_url: str = Field(default_factory=lambda: str(os.getenv("LLM_BASE_URL")))
    model: str = Field(default_factory=lambda: str(os.getenv("LLM_MODEL")))


class SecurityConfig(BaseModel):
    google_client_id: str = Field(
        default_factory=lambda: str(os.getenv("GOOGLE_CLIENT_ID"))
    )
    google_client_secret: str = Field(
        default_factory=lambda: str(os.getenv("GOOGLE_CLIENT_SECRET"))
    )
    jwt_secret: str = Field(default_factory=lambda: str(os.getenv("JWT_SECRET")))
    session_secret: str = Field(
        default_factory=lambda: str(os.getenv("SESSION_SECRET"))
    )


class AppConfig(BaseModel):
    backend_public_url: str = Field(
        default_factory=lambda: str(
            os.getenv("BACKEND_PUBLIC_URL", "http://localhost:8000")
        ).rstrip("/")
    )
    frontend_url: str = Field(
        default_factory=lambda: str(
            os.getenv("FRONTEND_URL", "http://localhost:5173")
        ).rstrip("/")
    )
    cors_origins: list[str] = Field(
        default_factory=lambda: _csv_env("CORS_ORIGINS", "http://localhost:5173")
    )


class Config(BaseModel):
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    rabbitmq: RabbitMQConfig = Field(default_factory=RabbitMQConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    app: AppConfig = Field(default_factory=AppConfig)


def create_config():
    return Config()
