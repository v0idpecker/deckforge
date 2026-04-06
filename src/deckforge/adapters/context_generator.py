from typing import List

from tatoebatools import ParallelCorpus

from deckforge.adapters.errors import ExternalServiceError


class ContextGenerator:
    def get_context_sentence(
        self, word: str | None, limit: int, sentence_lang: str, translation_lang: str
    ) -> List[dict]:
        lang_codes = {
            "english": "eng",
            "russian": "rus",
            "german": "deu",
            "spanish": "spa",
            "french": "fra",
            "italian": "ita",
        }

        src = lang_codes.get(sentence_lang, "eng")
        tgt = lang_codes.get(translation_lang, "rus")

        corpus = ParallelCorpus(src, tgt)

        examples = []

        for sentence, translation in corpus:
            try:
                if word is None or word.lower() in sentence.text.lower():
                    examples.append(
                        {
                            sentence_lang: sentence.text,
                            translation_lang: translation.text,
                        }
                    )

                    if len(examples) >= limit:
                        break

            except ConnectionError as e:
                raise ExternalServiceError(f"Failed to fetch context: {e}")

        return examples
