"""
Captures screenshots of all project source code files using Playwright.
Renders each file as syntax-highlighted HTML and takes a screenshot.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOTS_DIR = Path(__file__).resolve().parent / "screenshots" / "code"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# All important source code files
CODE_FILES = [
    # Task 1
    ("task1_crawler_pure_crawler", "task1_vertical_search/backend/crawler/pure_crawler.py"),
    ("task1_crawler_robots_check", "task1_vertical_search/backend/crawler/robots_check.py"),
    ("task1_crawler_http_client", "task1_vertical_search/backend/crawler/http_client.py"),
    ("task1_crawler_parsers", "task1_vertical_search/backend/crawler/parsers.py"),
    ("task1_ranking_vsm", "task1_vertical_search/backend/ranking/vector_space_model.py"),
    ("task1_utils_preprocessing", "task1_vertical_search/backend/utils/text_preprocessing.py"),
    ("task1_routes_api", "task1_vertical_search/backend/routes/api.py"),
    ("task1_database_mongo", "task1_vertical_search/backend/database/mongo_client.py"),
    ("task1_config_settings", "task1_vertical_search/backend/config/settings.py"),
    ("task1_run", "task1_vertical_search/backend/run.py"),
    # Task 2
    ("task2_clustering_kmeans", "task2_document_clustering/backend/clustering/kmeans_model.py"),
    ("task2_preprocessing", "task2_document_clustering/backend/preprocessing/text_preprocessing.py"),
    ("task2_routes_api", "task2_document_clustering/backend/routes/api.py"),
    ("task2_database_mongo", "task2_document_clustering/backend/database/mongo_client.py"),
    ("task2_config_settings", "task2_document_clustering/backend/config/settings.py"),
    ("task2_visualization_pca", "task2_document_clustering/backend/visualization/pca_plot.py"),
    ("task2_run", "task2_document_clustering/backend/run.py"),
    ("task2_scripts_build_dataset", "task2_document_clustering/scripts/build_dataset.py"),
    ("task2_scripts_train_model", "task2_document_clustering/scripts/train_model.py"),
    # Frontend
    ("frontend_app", "unified_frontend/app.py"),
    ("frontend_js", "unified_frontend/static/js/app.js"),
    ("frontend_css", "unified_frontend/static/css/style.css"),
    ("frontend_html", "unified_frontend/templates/index.html"),
]

def generate_code_html(filepath, code_text):
    """Generate dark-themed code HTML mimicking VS Code."""
    # Escape HTML
    code_text = code_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    # Add line numbers
    lines = code_text.split("\n")
    numbered_lines = []
    for i, line in enumerate(lines, 1):
        numbered_lines.append(
            f'<span class="line-num">{i:>4}</span>  {line}'
        )
    code_with_numbers = "\n".join(numbered_lines)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
<style>
    body {{
        background-color: #1e1e1e;
        color: #d4d4d4;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 11px;
        margin: 0;
        padding: 10px;
    }}
    .title-bar {{
        background: #2d2d2d;
        color: #cccccc;
        padding: 6px 12px;
        font-size: 12px;
        border-bottom: 1px solid #3c3c3c;
        margin: -10px -10px 10px -10px;
    }}
    pre {{
        margin: 0;
        white-space: pre;
        line-height: 1.5;
    }}
    .line-num {{
        color: #858585;
        user-select: none;
    }}
</style>
</head>
<body>
    <div class="title-bar">{filepath}</div>
    <pre>{code_with_numbers}</pre>
</body>
</html>"""
    return html


async def capture_all_code():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        for name, rel_path in CODE_FILES:
            full_path = PROJECT_ROOT / rel_path
            if not full_path.exists():
                print(f"  SKIP (not found): {rel_path}")
                continue
                
            code_text = full_path.read_text(encoding="utf-8", errors="replace")
            
            # Calculate needed height based on line count
            line_count = len(code_text.split("\n"))
            height = max(600, min(line_count * 18 + 60, 8000))
            
            html = generate_code_html(rel_path, code_text)
            
            # Write temp HTML
            temp_file = SCREENSHOTS_DIR / f"_temp_{name}.html"
            temp_file.write_text(html, encoding="utf-8")
            
            page = await browser.new_page(viewport={"width": 1000, "height": height})
            await page.goto(f"file:///{temp_file.resolve()}")
            await page.wait_for_timeout(300)
            
            screenshot_path = SCREENSHOTS_DIR / f"{name}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            await page.close()
            
            temp_file.unlink()  # Clean up temp
            print(f"  OK: {rel_path} -> {screenshot_path.name}")
        
        await browser.close()
    print(f"\nAll code screenshots saved to {SCREENSHOTS_DIR}")


if __name__ == "__main__":
    asyncio.run(capture_all_code())
