"""Generates the two conceptual architecture diagrams as real vector-quality
PNG figures (box-and-arrow flow diagrams), matching the pipelines actually
implemented in the codebase."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.font_manager import FontProperties
from pathlib import Path

OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)

VIOLET = "#5b3df0"
TEAL = "#0f9c92"
NAVY = "#1a2140"
BG = "#ffffff"
MUTED = "#5a6b7d"


def draw_pipeline(steps, title, out_path, col_widths=None):
    """steps: list of (label, sublabel, color) drawn top-to-bottom with arrows."""
    n = len(steps)
    fig_h = 1.1 * n + 1.2
    fig, ax = plt.subplots(figsize=(7.2, fig_h))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, n + 1)
    ax.axis("off")

    box_w, box_h = 7.6, 0.78
    x0 = (10 - box_w) / 2

    for i, (label, sub, color) in enumerate(steps):
        y = n - i - 0.5
        box = FancyBboxPatch(
            (x0, y - box_h / 2), box_w, box_h,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            linewidth=1.6, edgecolor=color, facecolor=color + "18",
        )
        ax.add_patch(box)
        ax.text(x0 + box_w / 2, y + 0.08, label, ha="center", va="center",
                 fontsize=11.5, fontweight="bold", color=NAVY)
        if sub:
            ax.text(x0 + box_w / 2, y - 0.20, sub, ha="center", va="center",
                     fontsize=8.3, color=MUTED)
        if i < n - 1:
            arrow = FancyArrowPatch(
                (x0 + box_w / 2, y - box_h / 2 - 0.02),
                (x0 + box_w / 2, y - 1 + box_h / 2 + 0.02),
                arrowstyle="-|>", mutation_scale=16, linewidth=1.6, color=NAVY,
            )
            ax.add_patch(arrow)

    ax.set_title(title, fontsize=13, fontweight="bold", color=NAVY, pad=14)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, facecolor=BG)
    plt.close(fig)
    print("saved", out_path)


task1_steps = [
    ("Coventry PurePortal Seed URL", "Centre for Healthcare and Community Transformation", VIOLET),
    ("Focused, Polite Crawler", "robots.txt compliance · crawl-delay · BFS over profile/publication links", VIOLET),
    ("Research Output + Profile Filtering", "keeps only pages confirming centre membership", VIOLET),
    ("Data Extraction", "title, authors, date, type, abstract, profile URLs", VIOLET),
    ("MongoDB Atlas", "research_outputs · profiles · crawl_logs · search_logs", NAVY),
    ("Text Preprocessing", "lowercase → tokenise → stop-word removal", TEAL),
    ("TF-IDF Vectorisation", "document-term matrix (scikit-learn TfidfVectorizer)", TEAL),
    ("Vector Space Model Index", "one vector per research output", TEAL),
    ("User Query", "same preprocessing + TF-IDF transform", VIOLET),
    ("Cosine Similarity Ranking", "query vector vs. every document vector", TEAL),
    ("Top-K = 10, Paginated Results", "clickable titles + author profile links", VIOLET),
    ("Unified Web Interface", "Flask REST API + browser frontend", NAVY),
]

task2_steps = [
    ("Academic News Dataset", "Greene & Cunningham (2006) BBC News corpus", VIOLET),
    ("Economics / Entertainment / Politics", "180 documents per category (540 total)", VIOLET),
    ("Dataset Validation", "≥150/category check before training proceeds", NAVY),
    ("Text Preprocessing", "clean → lowercase → tokenise → stop-words → Porter stemming", TEAL),
    ("TF-IDF Vectorisation", "document-term matrix (scikit-learn TfidfVectorizer)", TEAL),
    ("K-Means Clustering (K = 3)", "k-means++ init · n_init = 10 · Euclidean distance", TEAL),
    ("Cluster → Category Mapping", "majority vote against known labels", NAVY),
    ("Persisted Model Artifacts", "vectorizer + K-Means model + mapping (joblib)", NAVY),
    ("User Document Input", "sentence / paragraph typed by the user", VIOLET),
    ("Nearest Centroid Assignment", "existing model — never retrained on input", TEAL),
    ("Predicted Category", "Economics / Entertainment / Politics + distance", VIOLET),
    ("MongoDB Atlas — clustering_predictions", "every prediction persisted with a timestamp", NAVY),
]

draw_pipeline(task1_steps, "Figure 1 — Conceptual Architecture: Task 1 Vertical Search Engine",
              OUT / "figure_01_task1_conceptual_architecture.png")
draw_pipeline(task2_steps, "Figure 2 — Conceptual Architecture: Task 2 Document Clustering",
              OUT / "figure_02_task2_conceptual_architecture.png")
