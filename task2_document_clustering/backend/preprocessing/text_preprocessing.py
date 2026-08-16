"""
Text preprocessing pipeline for Task 2 (document clustering).

    Raw document
        -> Cleaning          (strip control characters / excess whitespace)
        -> Lowercasing
        -> Tokenisation       (split into alphabetic word tokens)
        -> Punctuation removal (non-alphabetic tokens are dropped as a
                                 side effect of the tokenisation regex)
        -> Stop-word removal  (scikit-learn's English stop-word list)
        -> Stemming            (Porter stemmer, so that "economy",
                                 "economic" and "economics" collapse to a
                                 single feature -- this measurably helps a
                                 topic-clustering task, unlike in Task 1
                                 where author *names* must stay intact)
        -> (TF-IDF is applied afterwards, in clustering/kmeans_model.py)

Every stage is a separate, named function so each step required by the
coursework brief's preprocessing diagram is independently inspectable and
testable.
"""
import re

from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

_stemmer = PorterStemmer()
_TOKEN_RE = re.compile(r"[a-zA-Z]{2,}")


def clean_text(text: str) -> str:
    """Strip control/whitespace noise from raw scraped/typed text."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def to_lowercase(text: str) -> str:
    return text.lower()


def tokenise(text: str) -> list[str]:
    """Tokenise into alphabetic words; this simultaneously discards
    punctuation, digits and symbols (punctuation removal)."""
    return _TOKEN_RE.findall(text)


def remove_stopwords(tokens: list[str]) -> list[str]:
    return [t for t in tokens if t not in ENGLISH_STOP_WORDS]


def stem_tokens(tokens: list[str]) -> list[str]:
    return [_stemmer.stem(t) for t in tokens]


def preprocess(text: str) -> str:
    """Run the full pipeline and return a whitespace-joined string of
    processed terms, ready to hand to TfidfVectorizer."""
    text = clean_text(text)
    text = to_lowercase(text)
    tokens = tokenise(text)
    tokens = remove_stopwords(tokens)
    tokens = stem_tokens(tokens)
    return " ".join(tokens)
