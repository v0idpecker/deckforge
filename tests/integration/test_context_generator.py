import allure
import pytest
from types import SimpleNamespace

from deckforge.adapters.context_generator import (
    PROMPT_VERSION,
    TARGET_WORD_FORM_KEY,
    SentenceItem,
    TranslationResponse,
)
from deckforge.adapters.errors import ExternalServiceError

pytestmark = pytest.mark.asyncio


def make_parsed(sentence: str, form: str, translation: str = "Кот спит."):
    return TranslationResponse(
        word="cat",
        sentences=[SentenceItem(sentence=sentence, translation=translation, target_word_form=form)],
    )


def wrap_response(parsed, content="assistant content"):
    message = SimpleNamespace(parsed=parsed, content=content, refusal=None)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class ScriptedLLMClient:
    def __init__(self, responses):
        self._responses = responses
        self.calls = 0

    @property
    def chat(self):
        return SimpleNamespace(completions=SimpleNamespace(parse=self._parse))

    async def _parse(self, **kwargs):
        response = self._responses[min(self.calls, len(self._responses) - 1)]
        self.calls += 1
        return response


def build_generator(responses) -> tuple:
    from deckforge.adapters.context_generator import ContextGenerator

    client = ScriptedLLMClient(responses)
    return ContextGenerator(client, model="fake-model"), client


@allure.feature("Context generator")
@allure.story("target word form")
async def test_valid_response_includes_target_word_form():
    parsed = make_parsed("The cat sleeps.", "cat")
    generator, _ = build_generator([wrap_response(parsed)])

    result = await generator.get_context_sentence("cat", 1, "english", "russian", "B1")

    assert result == [
        {
            "english": "The cat sleeps.",
            "russian": "Кот спит.",
            TARGET_WORD_FORM_KEY: "cat",
        }
    ]


@allure.feature("Context generator")
@allure.story("target word form")
async def test_invalid_word_form_triggers_correction_retry():
    bad_form = make_parsed("The cat sleeps.", "dog")
    good = make_parsed("The cat sleeps.", "cat")
    generator, client = build_generator([wrap_response(bad_form), wrap_response(good)])

    result = await generator.get_context_sentence("cat", 1, "english", "russian", "B1")

    assert client.calls == 2
    assert result[0][TARGET_WORD_FORM_KEY] == "cat"


@allure.feature("Context generator")
@allure.story("target word form")
async def test_word_form_failure_degrades_instead_of_raising():
    bad_form = make_parsed("The cat sleeps.", "dog")
    generator, client = build_generator([wrap_response(bad_form), wrap_response(bad_form)])

    result = await generator.get_context_sentence("cat", 1, "english", "russian", "B1")

    assert client.calls == 2
    assert result[0]["english"] == "The cat sleeps."
    assert result[0][TARGET_WORD_FORM_KEY] == ""


@allure.feature("Context generator")
@allure.story("target word form")
async def test_structural_failure_still_raises_external_service_error():
    wrong_count = TranslationResponse(word="cat", sentences=[])
    generator, client = build_generator([wrap_response(wrong_count), wrap_response(wrong_count)])

    with pytest.raises(ExternalServiceError):
        await generator.get_context_sentence("cat", 1, "english", "russian", "B1")

    assert client.calls == 2


@allure.feature("Context generator")
@allure.story("target word form")
async def test_word_form_matching_normalizes_punctuation_and_case():
    parsed = make_parsed("The CAT sleeps.", " cat. ")
    generator, _ = build_generator([wrap_response(parsed)])

    result = await generator.get_context_sentence("cat", 1, "english", "russian", "B1")

    assert result[0][TARGET_WORD_FORM_KEY] == " cat. "


@allure.feature("Context generator")
@allure.story("prompt version")
def test_prompt_version_bumped():
    assert PROMPT_VERSION == 2
