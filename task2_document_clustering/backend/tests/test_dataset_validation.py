"""
Confirms the real dataset built by scripts/build_dataset.py (persisted in
MongoDB and mirrored to dataset/processed/) satisfies the coursework's
minimum document-count requirement per category.
"""
import json

from config.settings import settings
from database.mongo_client import documents_col


def test_validation_report_file_exists_and_passes():
    assert settings.PROCESSED_DATASET_DIR.joinpath("dataset_validation_report.json").exists(), \
        "Run scripts/build_dataset.py before running this test."
    with open(settings.PROCESSED_DATASET_DIR / "dataset_validation_report.json", encoding="utf-8") as f:
        report = json.load(f)
    for row in report["rows"]:
        assert row["status"] == "PASS", f"{row['category']} failed dataset validation: {row}"


def test_mongodb_has_at_least_minimum_documents_per_category():
    for category in settings.CATEGORIES:
        count = documents_col().count_documents({"category": category})
        assert count >= settings.MIN_DOCS_PER_CATEGORY, f"{category} has only {count} documents in MongoDB"


def test_total_documents_meets_overall_minimum():
    total = documents_col().count_documents({})
    assert total >= settings.MIN_DOCS_PER_CATEGORY * len(settings.CATEGORIES)
