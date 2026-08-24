import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm

# Data exactly as requested
labels = [
    "Documents / vocabulary terms",
    "Number of clusters (K)",
    "Accuracy vs. known labels",
    "Precision (macro)",
    "Recall (macro)",
    "F1 (macro)",
    "Silhouette score",
    "Inertia"
]

values = [
    "540 / 290",
    "3",
    "93.0%",
    "0.9333",
    "0.9296",
    "0.9296",
    "0.0604",
    "431.15"
]

# Set up figure with a sleek dark theme
fig, ax = plt.subplots(figsize=(9, 5.5))
fig.patch.set_facecolor('#0d1117')
ax.set_facecolor('#0d1117')
ax.axis('off')

# Title
plt.title("Task 2 — K-Means Model Evaluation", color='white', pad=15, fontsize=18, fontweight='bold', fontfamily='sans-serif')

# Create table data
cell_text = [[l, v] for l, v in zip(labels, values)]

# Draw table
table = ax.table(cellText=cell_text, cellLoc='left', loc='center', edges='horizontal')
table.auto_set_font_size(False)
table.set_fontsize(14)
table.scale(1, 2.4)

# Style cells
for (row, col), cell in table.get_celld().items():
    cell.set_facecolor('#0d1117')
    cell.set_edgecolor('#21262d') # Subtle borders
    cell.set_text_props(fontfamily='sans-serif', fontsize=14)
    
    if col == 0:
        # Labels column (muted grey)
        cell.set_text_props(color='#8b949e')
        cell.get_text().set_ha('left')
        cell.PAD = 0.05
    elif col == 1:
        # Values column
        cell.get_text().set_ha('right')
        if labels[row] in ["Accuracy vs. known labels", "F1 (macro)"]:
            # Highlight key metrics in neon green
            cell.set_text_props(color='#10b981', fontweight='bold', fontsize=15)
        else:
            # Regular metrics in bright white
            cell.set_text_props(color='#f0f6fc', fontweight='bold')

# Adjust column widths manually for a perfect fit
table.auto_set_column_width([0, 1])

plt.tight_layout()
plt.savefig('../metrics_table.png', dpi=300, bbox_inches='tight', facecolor='#0d1117', pad_inches=0.3)
print("Successfully generated metrics_table.png")
