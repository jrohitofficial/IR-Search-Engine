"""Central configuration for the Task 2 document clustering backend."""
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    MONGODB_URI: str = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.environ.get("TASK2_DATABASE_NAME", "Task_2_Document_Clustering")

    CATEGORIES: list[str] = ["Economics", "Entertainment", "Politics"]
    MIN_DOCS_PER_CATEGORY: int = int(os.environ.get("MIN_DOCS_PER_CATEGORY", "150"))
    TARGET_DOCS_PER_CATEGORY: int = int(os.environ.get("TARGET_DOCS_PER_CATEGORY", "180"))
    N_CLUSTERS: int = 3

    TASK2_PORT: int = int(os.environ.get("TASK2_PORT", "5002"))

    BACKEND_DIR: Path = Path(__file__).resolve().parents[1]
    DATASET_DIR: Path = Path(__file__).resolve().parents[2] / "dataset"
    RAW_DATASET_DIR: Path = DATASET_DIR / "raw" / "bbc"
    PROCESSED_DATASET_DIR: Path = DATASET_DIR / "processed"
    MODELS_DIR: Path = BACKEND_DIR / "models_artifacts"
    FIGURES_DIR: Path = Path(__file__).resolve().parents[3] / "documentation" / "figures"

    VECTORIZER_PATH: Path = MODELS_DIR / "tfidf_vectorizer.joblib"
    KMEANS_MODEL_PATH: Path = MODELS_DIR / "kmeans_model.joblib"
    CLUSTER_MAPPING_PATH: Path = MODELS_DIR / "cluster_to_category.joblib"
    EVALUATION_REPORT_PATH: Path = MODELS_DIR / "evaluation_report.json"


settings = Settings()
settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
settings.PROCESSED_DATASET_DIR.mkdir(parents=True, exist_ok=True)
settings.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
