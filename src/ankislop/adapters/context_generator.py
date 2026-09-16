import logging
from typing import List

from openai import APIError, AsyncOpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from pydantic import BaseModel

from ankislop.adapters.errors import ExternalServiceError

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Ты — генератор учебных примеров для карточек Anki.
По заданному слову генерируешь указанное количество примеров предложений
на языке {source_lang} с переводом на {target_lang}.

Отвечай ТОЛЬКО валидным json, без markdown, без ```json, без пояснений.

Правила:
1. Предложения разнообразны по контексту и грамматической конструкции, не повторяй шаблоны.
2. Целевое слово естественно встроено (допустимы формы: время, число, падеж, степени сравнения — в зависимости от {source_lang}).
3. Уровень сложности — {difficulty}.
4. Перевод на {target_lang} литературный, не подстрочный.
5. В поле target_word_form укажи точную форму целевого слова, как она стоит в предложении: слово целиком, без знаков препинания и лишних пробелов.

Пример формата:
{{"word": "...", "sentences": [{{"sentence": "...", "translation": "...", "target_word_form": "..."}}]}}
"""

PROMPT_VERSION = 2

TARGET_WORD_FORM_KEY = "target_word_form"


def build_system_prompt(source_lang: str, target_lang: str, difficulty: str):
    return SYSTEM_PROMPT.format(
        source_lang=source_lang, target_lang=target_lang, difficulty=difficulty
    )


def build_user_prompt(word: str, limit: int):
    return f'Слово: "{word}"\nКоличество предложений: {limit}\nВерни json строго по описанной схеме.'


FORM_STRIP_CHARS = " \t\n\r.,!?;:\"'«»„“”()"


class SentenceItem(BaseModel):
    sentence: str
    translation: str
    target_word_form: str


class TranslationResponse(BaseModel):
    word: str
    sentences: List[SentenceItem]


class ContextGenerator:
    def __init__(self, client: AsyncOpenAI, model: str):
        self._client = client
        self.model = model

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
                TARGET_WORD_FORM_KEY: item.target_word_form,
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
        last_parsed = None
        for attempt in range(2):
            try:
                response = await self._client.chat.completions.parse(
                    model=self.model,
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
                last_parsed = parsed
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
        if self._has_valid_structure(last_parsed, limit):
            logger.warning(
                "LLM failed to return valid target_word_form for word '%s', "
                "degrading to sentences without word form",
                word,
            )
            if last_parsed:
                return self._sanitize_forms(last_parsed)
        raise ExternalServiceError(
            f"LLM failed to return a valid response for word '{word}' "
            f"(limit={limit}, difficulty={difficulty}) after 2 attempts"
        )

    @staticmethod
    def _has_valid_structure(parsed, limit: int) -> bool:
        return (
            isinstance(parsed, TranslationResponse) and len(parsed.sentences) == limit
        )

    @staticmethod
    def normalize_form(form: str) -> str:
        return form.strip(FORM_STRIP_CHARS)

    @classmethod
    def _is_valid_form(cls, sentence: str, form: str) -> bool:
        normalized = cls.normalize_form(form)
        return bool(normalized) and normalized.lower() in sentence.lower()

    @classmethod
    def _sanitize_forms(cls, parsed: TranslationResponse) -> TranslationResponse:
        for item in parsed.sentences:
            if not cls._is_valid_form(item.sentence, item.target_word_form):
                item.target_word_form = ""
        return parsed

    async def validate_response(self, parsed, limit: int):
        if not isinstance(parsed, TranslationResponse):
            raise ValueError("Ты не вернул валидный JSON: parsed is None")
        if len(parsed.sentences) != limit:
            raise ValueError(
                f"Ты не вернул нужное кол-во предложений: {len(parsed.sentences)} вместо {limit}"
            )
        invalid_indices = [
            i
            for i, item in enumerate(parsed.sentences)
            if not self._is_valid_form(item.sentence, item.target_word_form)
        ]
        if invalid_indices:
            raise ValueError(
                "В поле target_word_form укажи точную форму целевого слова, "
                "как она стоит в sentence, без знаков препинания. "
                f"Форма не найдена в предложении для индексов: {invalid_indices}"
            )
