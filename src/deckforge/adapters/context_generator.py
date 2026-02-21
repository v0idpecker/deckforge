from typing import List

from tatoebatools import ParallelCorpus


class ContextGenerator:
    def __init__(self, corpus: ParallelCorpus):
        self._corpus = corpus

    def get_context_sentence(self, word: str, limit: int) -> List[dict]:
        examples = []

        for sentence, translation in self._corpus:
            if word.lower() in sentence.text.lower():
                examples.append({"english": sentence.text, "russian": translation.text})

                if len(examples) >= limit:
                    break

        return examples
