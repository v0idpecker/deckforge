# DeckForge

DeckForge — сервис для изучающих иностранные языки. Вводите слова, выбираете язык и уровень сложности, и сервис собирает колоду карточек Anki: для каждого слова подбираются примеры предложений с переводом. Готовый файл импортируется в Anki.

## Как это работает

```mermaid
flowchart TB
    A[Пользователь] --> B[Backend API]
    B --> C[(PostgreSQL: task + outbox event)]
    C --> D[Relay]
    D --> E[pipeline_queue]
    E --> F[Worker: PROCESSING]
    F --> G[LLM: генерация примеров]
    G --> H[Файл .apkg]
    H -->|download| A
    F -->|error| S[Scheduler: RETRY_SCHEDULED]
    S -->|reschedule| C
```

## Стек

Python · FastAPI · PostgreSQL · RabbitMQ · React · OpenAI API

## Запуск

```bash
docker compose up --build
```

Перед запуском создайте в корне проекта файл `.env` с ключами для LLM и Google OAuth (список переменных есть в `src/deckforge/config.py`). Интерфейс будет доступен на `http://localhost:5173`.
