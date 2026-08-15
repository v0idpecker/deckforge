import allure
import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from deckforge.adapters.context_generator import PROMPT_VERSION
from deckforge.db.models.llm_cache import LLMCache
from deckforge.dto.llm_cache import LLMCacheCreateDTO, LLMCacheKeyDTO

pytestmark = pytest.mark.asyncio


def build_create_dto(word: str, result: list[dict], model: str = "fake-model"):
    return LLMCacheCreateDTO(
        word=word,
        sentence_lang="english",
        translation_lang="russian",
        difficulty="B1",
        limit=2,
        model=model,
        prompt_version=PROMPT_VERSION,
        result=result,
    )


@allure.feature("LLM cache")
@allure.story("ContextGenerationService caching")
async def test_context_gen_service_miss_then_hit(
    context_gen_service,
    fake_llm_generator,
    db_session: AsyncSession,
):
    first = await context_gen_service.get_context_sentence(
        word="cat",
        limit=2,
        sentence_lang="english",
        translation_lang="russian",
        difficulty="B1",
    )
    assert fake_llm_generator.calls == 1

    second = await context_gen_service.get_context_sentence(
        word="cat",
        limit=2,
        sentence_lang="english",
        translation_lang="russian",
        difficulty="B1",
    )

    # генератор не вызывался повторно, результат взят из кэша
    assert fake_llm_generator.calls == 1
    assert second == first

    # результат записан в кэш
    count = (
        await db_session.execute(select(func.count()).select_from(LLMCache))
    ).scalar_one()
    assert count == 1


@allure.feature("LLM cache")
@allure.story("ContextGenerationService caching")
async def test_context_gen_service_hit_does_not_call_generator(
    context_gen_service,
    fake_llm_generator,
    llm_cache_service,
):
    prefilled_result = [
        {"english": "prefilled sentence", "russian": "prefilled translation"}
    ]
    await llm_cache_service.create(build_create_dto("cat", prefilled_result))

    result = await context_gen_service.get_context_sentence(
        word="cat",
        limit=2,
        sentence_lang="english",
        translation_lang="russian",
        difficulty="B1",
    )

    assert fake_llm_generator.calls == 0
    assert result == prefilled_result


@allure.feature("LLM cache")
@allure.story("LLMCacheDAO")
async def test_cache_dao_create_twice_same_key_keeps_one_row_and_updates_result(
    llm_cache_dao,
    db_session: AsyncSession,
):
    first = build_create_dto("cat", [{"english": "first sentence"}])
    second = build_create_dto("cat", [{"english": "second sentence"}])

    await llm_cache_dao.create(db_session, first)
    await db_session.commit()
    await llm_cache_dao.create(db_session, second)
    await db_session.commit()

    key = dict(
        word="cat",
        sentence_lang="english",
        translation_lang="russian",
        difficulty="B1",
        limit=2,
        model="fake-model",
        prompt_version=PROMPT_VERSION,
    )
    count = (
        await db_session.execute(
            select(func.count()).select_from(LLMCache).filter_by(**key)
        )
    ).scalar_one()
    assert count == 1

    rows = (await db_session.execute(select(LLMCache).filter_by(**key))).scalars().all()
    assert len(rows) == 1
    assert rows[0].result == [{"english": "second sentence"}]


@allure.feature("LLM cache")
@allure.story("LLMCacheDAO")
async def test_cache_dao_get_by_key_miss_returns_none(
    llm_cache_dao,
    db_session: AsyncSession,
):
    key = LLMCacheKeyDTO(
        word="absent-word",
        sentence_lang="english",
        translation_lang="russian",
        difficulty="B1",
        limit=2,
        model="fake-model",
        prompt_version=PROMPT_VERSION,
    )

    result = await llm_cache_dao.get_by_key(db_session, key)

    assert result is None
