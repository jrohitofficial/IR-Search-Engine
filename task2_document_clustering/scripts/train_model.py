"""
Trains the TF-IDF + K-Means clustering model on the corpus stored in
MongoDB, evaluates it against the known category labels, generates the
2D cluster visualisation, and persists the vectorizer/model/mapping to
disk so the running API never retrains on a live request.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from clustering.kmeans_model import train  # noqa: E402
from config.settings import settings  # noqa: E402
from database.mongo_client import documents_col  # noqa: E402
from utils.logging_setup import configure_logging  # noqa: E402
from visualization.pca_plot import generate_cluster_plot  # noqa: E402


def main():
    configure_logging()

    documents = list(documents_col().find({}, {"content": 1, "category": 1, "title": 1, "document_id": 1}))
    if not documents:
        print("No documents found in MongoDB. Run scripts/build_dataset.py first.")
        sys.exit(1)

    print(f"Loaded {len(documents)} documents from MongoDB for training.")
    result = train(documents)

    # Pass the original texts and true labels to the visualisation
    plot_path = generate_cluster_plot(
        X=result["X"],
        cluster_labels=result["cluster_labels"],
        true_categories=result["true_categories"],
        cluster_to_category=result["cluster_to_category"],
        titles=[d.get("title", "") for d in result["documents"]]
    )

    print("\n=== Cluster -> Category mapping ===")
    print(json.dumps(result["cluster_to_category"], indent=2))

    print("\n=== Evaluation ===")
    print(json.dumps(result["evaluation"], indent=2))

    print(f"\nVisualisation saved to: {plot_path}")
    print(f"Model artifacts saved to: {settings.MODELS_DIR}")


if __name__ == "__main__":
    main()
