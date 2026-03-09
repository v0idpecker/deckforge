from nltk.stem import WordNetLemmatizer

from deckforge.adapters.errors import ExternalServiceError


class Normalizer:
    def __init__(self, lemmatizer: WordNetLemmatizer):
        self._lemmatizer = lemmatizer

    def lemmatize_word(self, word: str):
        try:
            return self._lemmatizer.lemmatize(word)
        except LookupError as e:
            raise ExternalServiceError(f"Failed to lemmatize word '{word}': {str(e)}")
        except TypeError as e:
            raise ExternalServiceError(
                f"Failed to lemmatize word '{word}': {str(e)}",
            )
