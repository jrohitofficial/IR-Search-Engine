"""
Builds the Task 2 labelled corpus (Economics / Entertainment / Politics)
from the Greene & Cunningham BBC News full-text dataset.

Data source and licence (Option B: "a legitimate existing dataset" --
chosen deliberately over live scraping of bbc.co.uk, whose own robots.txt
explicitly states "No scraping, crawling, or systematic extraction of
content" and "No creating datasets from BBC content", and which blocks
several AI-related crawlers by name):

    D. Greene and P. Cunningham. "Practical Solutions to the Problem of
    Diagonal Dominance in Kernel Document Clustering." Proceedings of the
    23rd International Conference on Machine Learning (ICML), 2006.
    Dataset page: http://mlg.ucd.ie/datasets/bbc.html
    "These datasets are made available for non-commercial and research
    purposes only." Original articles (2004-2005): copyright BBC.

The dataset's "business" category is used for the coursework's
"Economics" category (news outlets commonly file macroeconomic/monetary
policy reporting under a "business" desk; the article content itself is
economics reporting).

For each of the three required categories, the TARGET_DOCS_PER_CATICLE
longest available articles are kept (coursework guidance: "the longer is
usually the better"), each stored with its original filename as
document_id, its first line as title, full text as content, and the
academic citation above as source/source_url.
"""
import csv
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from config.settings import settings  # noqa: E402
from database.mongo_client import documents_col, ensure_indexes  # noqa: E402

CATEGORY_FOLDER_MAP = {
    "Economics": "business",
    "Entertainment": "entertainment",
    "Politics": "politics",
}
SOURCE_CITATION = (
    "Greene, D., & Cunningham, P. (2006). Practical Solutions to the "
    "Problem of Diagonal Dominance in Kernel Document Clustering. "
    "Proceedings of the 23rd International Conference on Machine "
    "Learning (ICML 2006)."
)
SOURCE_URL = "http://mlg.ucd.ie/datasets/bbc.html"


def load_category_files(category: str) -> list[dict]:
    folder = settings.RAW_DATASET_DIR / CATEGORY_FOLDER_MAP[category]
    docs = []
    for path in sorted(folder.glob("*.txt")):
        # The original archive is Windows-1252 encoded (curly quotes, £ signs).
        raw = path.read_text(encoding="cp1252", errors="replace")
        lines = raw.splitlines()
        title = lines[0].strip() if lines else path.stem
        content = raw.strip()
        docs.append({
            "document_id": f"{CATEGORY_FOLDER_MAP[category]}-{path.stem}",
            "title": title,
            "content": content,
            "category": category,
            "source": SOURCE_CITATION,
            "source_url": SOURCE_URL,
            "collection_date": datetime.now(timezone.utc).isoformat(),
            "original_publication_period": "2004-2005",
            "word_count": len(content.split()),
        })
    return docs


def select_top_n(docs: list[dict], n: int) -> list[dict]:
    """Prefer longer, information-richer documents, as the brief advises."""
    return sorted(docs, key=lambda d: d["word_count"], reverse=True)[:n]


def main():
    ensure_indexes()

    all_selected = []
    report_rows = []

    for category in settings.CATEGORIES:
        available = load_category_files(category)
        selected = select_top_n(available, settings.TARGET_DOCS_PER_CATEGORY)
        all_selected.extend(selected)

        status = "PASS" if len(selected) >= settings.MIN_DOCS_PER_CATEGORY else "FAIL"
        report_rows.append({
            "category": category,
            "required": settings.MIN_DOCS_PER_CATEGORY,
            "available_in_source": len(available),
            "actual_selected": len(selected),
            "status": status,
        })

    total = len(all_selected)
    total_status = "PASS" if total >= settings.MIN_DOCS_PER_CATEGORY * len(settings.CATEGORIES) else "FAIL"
    report_rows.append({
        "category": "TOTAL",
        "required": settings.MIN_DOCS_PER_CATEGORY * len(settings.CATEGORIES),
        "available_in_source": sum(r["available_in_source"] for r in report_rows),
        "actual_selected": total,
        "status": total_status,
    })

    print("\nDataset validation report")
    print(f"{'Category':<15}{'Required':>10}{'Available':>12}{'Selected':>10}{'Status':>8}")
    for row in report_rows:
        print(f"{row['category']:<15}{row['required']:>10}{row['available_in_source']:>12}{row['actual_selected']:>10}{row['status']:>8}")

    if any(r["status"] == "FAIL" for r in report_rows):
        print("\nDataset validation FAILED. Aborting before writing to MongoDB.")
        sys.exit(1)

    # Persist to MongoDB (upsert by document_id so re-running is idempotent).
    inserted, updated = 0, 0
    for doc in all_selected:
        result = documents_col().update_one(
            {"document_id": doc["document_id"]}, {"$set": doc}, upsert=True
        )
        if result.upserted_id is not None:
            inserted += 1
        else:
            updated += 1

    # Also write a local CSV/JSON snapshot for the processed dataset folder,
    # and a machine-readable validation report used by tests / documentation.
    csv_path = settings.PROCESSED_DATASET_DIR / "dataset.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_selected[0].keys()))
        writer.writeheader()
        writer.writerows(all_selected)

    report_path = settings.PROCESSED_DATASET_DIR / "dataset_validation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({"generated_at": datetime.now(timezone.utc).isoformat(), "rows": report_rows}, f, indent=2)

    print(f"\nMongoDB: {inserted} inserted, {updated} updated in 'clustering_documents'.")
    print(f"CSV snapshot written to {csv_path}")
    print(f"Validation report written to {report_path}")


if __name__ == "__main__":
    main()
