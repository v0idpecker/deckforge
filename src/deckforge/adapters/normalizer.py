from nltk.stem import WordNetLemmatizer


class Normilizer:
    def __init__(self, lemmatizer: WordNetLemmatizer):
        self._lemmatizer = lemmatizer

    def lemmatize_word(self, word):
        return self._lemmatizer.lemmatize(word)
