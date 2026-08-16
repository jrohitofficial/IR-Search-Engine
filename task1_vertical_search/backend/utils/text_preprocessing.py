"""
Shared text preprocessing pipeline applied identically to both crawled
documents and user queries, as required by the coursework brief
("apply the required pre-processing tasks to both the crawled data and
the users' queries").

Pipeline: raw text -> lowercase -> tokenise (alphabetic tokens only) ->
stop-word removal -> rejoin.

Stemming/lemmatisation is deliberately NOT applied here (unlike in Task 2):
Task 1 queries frequently target author *names* (e.g. "Deborah Lycett"),
and aggressive stemming can distort proper nouns and reduce precision for
name-based retrieval, which is an explicit coursework requirement. This is
a documented design decision, not an oversight.
"""
import re

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

_TOKEN_RE = re.compile(r"[a-zA-Z]{2,}")


def preprocess(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    tokens = _TOKEN_RE.findall(text)
    tokens = [t for t in tokens if t not in ENGLISH_STOP_WORDS]
    return " ".join(tokens)
