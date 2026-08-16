"""
Parser tests run against real, saved HTML captured from
pureportal.coventry.ac.uk on 2026-08-15 (see tests/fixtures/), so they are
deterministic and do not depend on the live site being reachable.
"""
from conftest import FIXTURES_DIR

from crawler.parsers import extract_links, parse_profile_detail, parse_publication_detail

SEED_URL = "https://pureportal.coventry.ac.uk/en/organisations/centre-for-healthcare-and-community-transformation/"
PUB_URL = "https://pureportal.coventry.ac.uk/en/publications/a-cross-sectional-study-of-postgraduate-students-mental-well-bein/"
PERSON_URL = "https://pureportal.coventry.ac.uk/en/persons/sally-abbott/"


def _read(name):
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def test_extract_links_finds_publications_and_persons():
    html = _read("seed_page.html")
    links = extract_links(html, SEED_URL)
    assert len(links["publications"]) > 0
    assert len(links["persons"]) > 0
    assert all(u.startswith("https://pureportal.coventry.ac.uk/en/publications/") for u in links["publications"])
    assert all(u.startswith("https://pureportal.coventry.ac.uk/en/persons/") for u in links["persons"])


def test_parse_publication_detail_extracts_required_fields():
    html = _read("pub_detail.html")
    record = parse_publication_detail(html, PUB_URL, SEED_URL)

    assert "Mental Well-Being" in record["title"]
    assert "Deborah Lycett" in record["authors"]
    assert any("deborah-lycett" in u for u in record["author_profiles"])
    assert record["is_centre_output"] is True
    assert record["publication_date"]  # non-empty
    assert record["document_url"] == PUB_URL
    assert record["description"]  # abstract extracted


def test_parse_profile_detail_extracts_required_fields():
    html = _read("person_sally.html")
    record = parse_profile_detail(html, PERSON_URL, SEED_URL)

    assert record["name"] == "Sally Abbott"
    assert record["role"] == "Assistant Professor"
    assert record["department"] == "Centre for Healthcare and Community Transformation"
    assert record["is_centre_member"] is True
    assert len(record["related_research_outputs"]) > 0
