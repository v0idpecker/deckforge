from typing import List


class ContextGenerator:
    """Stub implementation that returns fixed example sentences.

    No external calls are made, so the pipeline no longer depends on
    the Tatoeba network downloads. TODO: replace with a real generator
    (e.g. LLM-based) keeping the same interface.
    """

    def get_context_sentence(
        self, word: str | None, limit: int, sentence_lang: str, translation_lang: str
    ) -> List[dict]:
        lookup_word = word or "word"
        return [
            {
                sentence_lang: f"{lookup_word}: this is a stub sentence.",
                translation_lang: f"{lookup_word}: это предложение-заглушка.",
            }
            for _ in range(limit)
        ]
