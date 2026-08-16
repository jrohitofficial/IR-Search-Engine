"""
Unit tests for the TF-IDF / cosine-similarity Vector Space Model ranking
engine. MongoDB access is monkeypatched with an in-memory fake collection
so these tests are fast, deterministic and require no network/database.
"""
import pytest
from bson import ObjectId

import ranking.vector_space_model as vsm_module
from ranking.vector_space_model import VectorSpaceSearchEngine


class FakeCollection:
    def __init__(self, docs):
        self._docs = docs

    def find(self, *args, **kwargs):
        return list(self._docs)


def make_doc(title, content, authors=None, doc_url=None):
    authors = authors or []
    # Mirror crawler/parsers.py's real behaviour: the searchable "content"
    # field is built from title + description + authors, so author names
    # are indexed too (this is what makes author-name search work without
    # any special-cased ranking boost).
    full_content = " ".join([title, content] + authors)
    return {
        "_id": ObjectId(),
        "title": title,
        "content": full_content,
        "authors": authors,
        "author_profiles": [],
        "publication_date": "2026",
        "publication_type": "Article",
        "journal": "",
        "description": content[:50],
        "document_url": doc_url or f"https://pureportal.coventry.ac.uk/en/publications/{title.lower().replace(' ', '-')}/",
    }


@pytest.fixture
def engine(monkeypatch):
    docs = [
        make_doc("Digital health interventions", "digital health mobile app intervention wellbeing", authors=["Gemma Pearce"]),
        make_doc("Mental health in students", "mental health postgraduate students stress wellbeing", authors=["Sally Abbott"]),
        make_doc("Diabetes self-management", "diabetes glucose monitoring chronic kidney disease", authors=["Adeniyi Fagbamigbe"]),
    ]
    monkeypatch.setattr(vsm_module, "research_outputs_col", lambda: FakeCollection(docs))
    eng = VectorSpaceSearchEngine()
    eng.build_index()
    return eng


def test_index_builds_from_available_documents(engine):
    assert engine.is_ready


def test_keyword_search_ranks_relevant_document_first(engine):
    result = engine.search("mental health students", page=1, limit=10)
    assert result["total_results"] >= 1
    assert result["results"][0]["title"] == "Mental health in students"
    assert result["results"][0]["cosine_similarity"] > 0


def test_author_name_search_returns_matching_publication(engine):
    result = engine.search("Adeniyi Fagbamigbe", page=1, limit=10)
    assert result["total_results"] >= 1
    assert result["results"][0]["title"] == "Diabetes self-management"


def test_results_sorted_descending_by_cosine_similarity(engine):
    result = engine.search("health wellbeing", page=1, limit=10)
    scores = [r["cosine_similarity"] for r in result["results"]]
    assert scores == sorted(scores, reverse=True)


def test_no_match_returns_empty_results(engine):
    result = engine.search("quantum cryptography blockchain", page=1, limit=10)
    assert result["total_results"] == 0
    assert result["results"] == []


def test_empty_query_returns_empty_results(engine):
    result = engine.search("", page=1, limit=10)
    assert result["total_results"] == 0


def test_pagination_respects_top_k_limit(monkeypatch):
    docs = [make_doc(f"Health study {i}", "health wellbeing study intervention") for i in range(15)]
    monkeypatch.setattr(vsm_module, "research_outputs_col", lambda: FakeCollection(docs))
    eng = VectorSpaceSearchEngine()
    eng.build_index()

    page1 = eng.search("health wellbeing", page=1, limit=10)
    assert len(page1["results"]) == 10
    assert page1["total_results"] == 15
    assert page1["total_pages"] == 2

    page2 = eng.search("health wellbeing", page=2, limit=10)
    assert len(page2["results"]) == 5
