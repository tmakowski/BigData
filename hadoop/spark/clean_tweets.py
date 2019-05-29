from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from typing import List


def clean_text(text: str) -> List[str]:
    stop_words = stopwords.words('english')

    tokens = word_tokenize(text)
    words = [word.lower() for word in tokens if word.isalpha()]
    words = [w for w in words if not w in stop_words]

    return words
