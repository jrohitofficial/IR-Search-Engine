import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _render_terminal import render  # noqa: E402

EVID = Path(__file__).parent / "evidence"

jobs = [
    ("task1_crawl_log_excerpt.txt", "PowerShell — python run.py --crawl  (task1_vertical_search/backend)", "term_task1_crawl.png"),
    ("task1_pytest.txt", "PowerShell — pytest -v  (task1_vertical_search/backend)", "term_task1_pytest.png"),
    ("task2_build_dataset_output.txt", "PowerShell — python build_dataset.py  (task2_document_clustering/scripts)", "term_task2_build_dataset.png"),
    ("task2_train_model_output.txt", "PowerShell — python train_model.py  (task2_document_clustering/scripts)", "term_task2_train_model.png"),
    ("task2_pytest.txt", "PowerShell — pytest -v  (task2_document_clustering/backend)", "term_task2_pytest.png"),
]

for src, title, out in jobs:
    text = (EVID / src).read_text(encoding="utf-8")
    render(text, title, out)
