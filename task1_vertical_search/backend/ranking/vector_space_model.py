"""
Vector Space Model ranking engine (TF-IDF + cosine similarity), as
mandated by the coursework brief.

Pipeline:
    Documents -> preprocessing -> TF-IDF -> document-term matrix
    Query     -> SAME preprocessing -> TF-IDF query vector
    ranking   -> cosine_similarity(query_vector, document_matrix)
    result    -> sorted descending by similarity, top-K, paginated

TF-IDF definitions implemented via scikit-learn's TfidfVectorizer:
    TF(t,d)   = raw count of term t in document d (sklearn default:
                'term frequency', optionally sublinear)
    IDF(t)    = ln((1 + N) / (1 + df(t))) + 1   (scikit-learn's smoothed
                IDF, a numerically-stable variant of the classical
                IDF(t) = log(N / df(t)) formula taught in IR courses)
    TF-IDF(t,d) = TF(t,d) * IDF(t), then each document vector is
                L2-normalised so that cosine similarity reduces to a dot
                product.
Why TF-IDF/VSM is appropriate here: the corpus is small, heterogeneous
(titles, abstracts, author names) and free-text queries may be either
topical keywords or a person's name. TF-IDF naturally down-weights
common academic boilerplate terms while up-weighting rare, discriminating
terms (a specific author's surname, a specific clinical condition),
which is exactly the retrieval behaviour Google-Scholar-style search
needs without requiring any training data or external model.
"""
import logging
import threading

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from database.mongo_client import research_outputs_col
from utils.text_preprocessing import preprocess

logger = logging.getLogger("task1.ranking")


class VectorSpaceSearchEngine:
    def __init__(self):
        self._lock = threading.Lock()
        self._vectorizer: TfidfVectorizer | None = None
        self._doc_matrix = None
        self._documents: list[dict] = []

    def build_index(self) -> int:
        """(Re)build the TF-IDF index from the current contents of the
        research_outputs collection. Returns the number of documents indexed."""
        with self._lock:
            docs = list(research_outputs_col().find({}))
            corpus = [preprocess(d.get("content", "")) for d in docs]

            if not corpus or all(c == "" for c in corpus):
                self._vectorizer = None
                self._doc_matrix = None
                self._documents = []
                logger.warning("No documents available to build the search index.")
                return 0

            vectorizer = TfidfVectorizer()
            matrix = vectorizer.fit_transform(corpus)

            self._vectorizer = vectorizer
            self._doc_matrix = matrix
            self._documents = docs
            logger.info(
                "TF-IDF index built: %d documents, %d vocabulary terms.",
                matrix.shape[0], matrix.shape[1],
            )
            return len(docs)

    @property
    def is_ready(self) -> bool:
        return self._vectorizer is not None and self._doc_matrix is not None

    def search(self, query: str, page: int = 1, limit: int = 10) -> dict:
        if not self.is_ready:
            self.build_index()

        query_clean = preprocess(query)
        if not self.is_ready or not query_clean:
            return {"query": query, "total_results": 0, "page": page, "limit": limit, "total_pages": 0, "results": []}

        query_vector = self._vectorizer.transform([query_clean])
        similarities = cosine_similarity(query_vector, self._doc_matrix).flatten()

        ranked_indices = np.argsort(-similarities)
        ranked = [(idx, float(similarities[idx])) for idx in ranked_indices if similarities[idx] > 0.0]

        total_results = len(ranked)
        total_pages = max(1, (total_results + limit - 1) // limit) if total_results else 0
        start = (page - 1) * limit
        end = start + limit
        page_slice = ranked[start:end]

        results = []
        for idx, score in page_slice:
            doc = self._documents[idx]
            results.append({
                "id": str(doc["_id"]),
                "title": doc.get("title", ""),
                "authors": doc.get("authors", []),
                "author_profiles": doc.get("author_profiles", []),
                "publication_date": doc.get("publication_date", ""),
                "publication_type": doc.get("publication_type", ""),
                "journal": doc.get("journal", ""),
                "description": doc.get("description", ""),
                "document_url": doc.get("document_url", ""),
                "cosine_similarity": round(score, 4),
            })

        return {
            "query": query,
            "total_results": total_results,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "results": results,
        }


search_engine = VectorSpaceSearchEngine()
