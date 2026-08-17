"""
2D visualisation of the K-Means clustering result.

TF-IDF vectors are extremely high-dimensional (one dimension per
vocabulary term), so they cannot be plotted directly. Principal Component
Analysis (PCA) is used purely to project each document vector down to the
2 directions of greatest variance for plotting -- PCA plays no role in
the clustering decision itself (K-Means was already fit on the full
TF-IDF matrix in clustering/kmeans_model.py).
"""
import logging

import matplotlib
matplotlib.use("Agg")  # headless rendering, no display required
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

from config.settings import settings

logger = logging.getLogger("task2.visualization")

CATEGORY_COLORS = {"Economics": "#3b82f6", "Entertainment": "#a855f7", "Politics": "#10b981"}

import json
def generate_cluster_plot(X, cluster_labels, true_categories, cluster_to_category, titles=None, out_path=None) -> str:
    out_path = out_path or (settings.FIGURES_DIR / "figure_task2_kmeans_clusters.png")

    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X.toarray())

    fig, ax = plt.subplots(figsize=(9, 5), facecolor='none')
    ax.set_facecolor('none')
    ax.grid(color='#2a2d3e', linestyle='-', linewidth=0.5, zorder=0)

    for category in settings.CATEGORIES:
        mask = [c == category for c in true_categories]
        xs = [coords[i, 0] for i, m in enumerate(mask) if m]
        ys = [coords[i, 1] for i, m in enumerate(mask) if m]
        ax.scatter(xs, ys, label=f"{category}", color=CATEGORY_COLORS[category],
                   s=35, alpha=0.9, edgecolor="none", zorder=3)

    explained = pca.explained_variance_ratio_
    ax.set_xlabel(f"PCA Component 1", color='#64748b', fontsize=9)
    ax.set_ylabel(f"PCA Component 2", color='#64748b', fontsize=9)
    ax.tick_params(colors='none') # Hide ticks
    
    for spine in ax.spines.values():
        spine.set_color('#2a2d3e')

    fig.tight_layout()
    fig.savefig(out_path, dpi=150, transparent=True)
    plt.close(fig)

    # Save PCA coordinates to JSON for frontend interactive plotting
    pca_data = []
    titles = titles or ["Untitled"] * len(true_categories)
    for i, category in enumerate(true_categories):
        pca_data.append({
            "x": float(coords[i, 0]),
            "y": float(coords[i, 1]),
            "category": category,
            "title": titles[i]
        })
    json_path = settings.MODELS_DIR / "pca_data.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(pca_data, f)
    logger.info("PCA data saved to %s", json_path)

    logger.info("Cluster visualisation saved to %s", out_path)
    return str(out_path)
