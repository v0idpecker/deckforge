from typing import List

from openai import APIError, AsyncOpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from pydantic import BaseModel

from deckforge.adapters.errors import ExternalServiceError

SYSTEM_PROMPT = """Ты — генератор учебных примеров для карточек Anki.
По заданному слову генерируешь указанное количество примеров предложений
на языке {source_lang} с переводом на {target_lang}.

Отвечай ТОЛЬКО валидным json, без markdown, без ```json, без пояснений.

Правила:
1. Предложения разнообразны по контексту и грамматической конструкции, не повторяй шаблоны.
2. Целевое слово естественно встроено (допустимы формы: время, число, падеж, степени сравнения — в зависимости от {source_lang}).
3. Уровень сложности — {difficulty}.
4. Перевод на {target_lang} литературный, не подстрочный.

Пример формата:
{{"word": "...", "sentences": [{{"sentence": "...", "translation": "..."}}]}}
"""


def build_system_prompt(source_lang: str, target_lang: str, difficulty: str):
    return SYSTEM_PROMPT.format(
        source_lang=source_lang, target_lang=target_lang, difficulty=difficulty
    )


def build_user_prompt(word: str, limit: int):
    return f'Слово: "{word}"\nКоличество предложений: {limit}\nВерни json строго по описанной схеме.'


class SentenceItem(BaseModel):
    sentence: str
    translation: str


class TranslationResponse(BaseModel):
    word: str
    sentences: List[SentenceItem]


class ContextGenerator:
    def __init__(self, client: AsyncOpenAI, model: str):
        self._client = client
        self._model = model

    async def get_context_sentence(
        self,
        word: str,
        limit: int,
        sentence_lang: str,
        translation_lang: str,
        difficulty: str,
    ) -> List[dict]:
        items = await self.llm_request(
            sentence_lang, translation_lang, word, limit, difficulty
        )
        return [
            {
                sentence_lang: item.sentence,
                translation_lang: item.translation,
            }
            for item in items.sentences
        ]

    async def llm_request(
        self,
        sentence_lang: str,
        translation_lang: str,
        word: str,
        limit: int,
        difficulty: str,
    ) -> TranslationResponse:
        system_msg = ChatCompletionSystemMessageParam(
            role="system",
            content=build_system_prompt(sentence_lang, translation_lang, difficulty),
        )
        user_msg = ChatCompletionUserMessageParam(
            role="user", content=build_user_prompt(word, limit)
        )
        messages = [system_msg, user_msg]
        for attempt in range(2):
            try:
                response = await self._client.chat.completions.parse(
                    model=self._model,
                    messages=messages,
                    response_format=TranslationResponse,
                )
            except APIError as err:
                raise ExternalServiceError(f"LLM API failed: {err}")

            parsed = response.choices[0].message.parsed
            content = response.choices[0].message.content

            if parsed is None or content is None:
                refusal = response.choices[0].message.refusal
                assistant_text = content or refusal or "(пустой ответ)"
                messages.append(
                    ChatCompletionAssistantMessageParam(
                        role="assistant", content=assistant_text
                    )
                )
                messages.append(
                    ChatCompletionUserMessageParam(
                        role="user",
                        content="Ты не вернул валидный JSON по схеме. Верни исправленный JSON.",
                    )
                )
                continue

            try:
                await self.validate_response(parsed, limit)
                return parsed
            except ValueError as err:
                messages.append(
                    ChatCompletionAssistantMessageParam(
                        role="assistant", content=content
                    )
                )
                messages.append(
                    ChatCompletionUserMessageParam(
                        role="user",
                        content=(
                            f"Твой предыдущий ответ невалиден. Ошибка: \n{str(err)}\n\n"
                            "Верни исправленный JSON, строго соответствующий схеме, "
                            "без пояснений и markdown-разметки."
                        ),
                    )
                )
                continue
        raise ExternalServiceError

    async def validate_response(self, parsed, limit: int):
        if not isinstance(parsed, TranslationResponse):
            raise ValueError("Ты не вернул валидный JSON: parsed is None")
        if len(parsed.sentences) != limit:
            raise ValueError(
                f"Ты не вернул нужное кол-во предложений: {len(parsed.sentences)} вместо {limit}"
            )
