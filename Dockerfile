FROM python:3.12-slim
WORKDIR /app

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y gcc

RUN pip install poetry
COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,target=/root/.cache/pypoetry \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-root

COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .

RUN apt-get update && apt-get install -y gcc unzip

ENV NLTK_DATA=/usr/local/share/nltk_data

COPY docker/nltk_data/ /tmp/nltk_data/
RUN mkdir -p ${NLTK_DATA}/corpora \
    && unzip -q /tmp/nltk_data/wordnet.zip -d ${NLTK_DATA}/corpora \
    && unzip -q /tmp/nltk_data/omw-1.4.zip -d ${NLTK_DATA}/corpora \
    && rm -rf /tmp/nltk_data

ENV PYTHONPATH=/app/src
CMD ["sh", "-c", "alembic upgrade head && uvicorn deckforge.main:app --host 0.0.0.0 --port 8000"]
