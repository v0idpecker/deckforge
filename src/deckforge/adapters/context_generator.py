from typing import List

from tatoebatools import ParallelCorpus

from deckforge.adapters.errors import ExternalServiceError


class ContextGenerator:
    def __init__(self, corpus: ParallelCorpus):
        self._corpus = corpus

    def get_context_sentence(self, word: str | None, limit: int) -> List[dict]:
        examples = []

        for sentence, translation in self._corpus:
            try:
                if word is None or word.lower() in sentence.text.lower():
                    examples.append(
                        {"english": sentence.text, "russian": translation.text}
                    )

                    if len(examples) >= limit:
                        break

            except ConnectionError as e:
                raise ExternalServiceError(f"Failed to fetch context: {e}")

        return examples
