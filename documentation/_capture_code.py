"""
Generate macOS VS Code-style code screenshots.
Fixes: proper syntax highlighting, full width, split long files into parts.
"""
import asyncio
import html as html_mod
from pathlib import Path
from playwright.async_api import async_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SNIPPETS_DIR = Path(__file__).resolve().parent / "screenshots" / "snippets"
CODE_DIR     = Path(__file__).resolve().parent / "screenshots" / "code"
SNIPPETS_DIR.mkdir(parents=True, exist_ok=True)
CODE_DIR.mkdir(parents=True, exist_ok=True)

MAX_LINES_PER_PART = 80  # Split long files into parts of this many lines


def highlight_line(line: str) -> str:
    """Highlight a single line of Python code using character-level scanning."""
    # Escape the entire line for HTML first
    escaped = html_mod.escape(line)
    
    result = []
    i = 0
    chars = escaped
    n = len(chars)
    
    while i < n:
        # Check for comment
        if chars[i] == '#':
            result.append(f'<span class="cmt">{chars[i:]}</span>')
            break
        
        # Check for strings
        if chars[i] in ('"', "'"):
            quote = chars[i]
            # Check for triple quote
            triple = quote * 3
            if chars[i:i+3] == triple:
                end = chars.find(triple, i+3)
                if end == -1:
                    result.append(f'<span class="str">{chars[i:]}</span>')
                    break
                else:
                    result.append(f'<span class="str">{chars[i:end+3]}</span>')
                    i = end + 3
                    continue
            else:
                # Find end of string
                j = i + 1
                while j < n and chars[j] != quote:
                    if chars[j] == '\\':
                        j += 2
                    else:
                        j += 1
                if j < n:
                    j += 1
                result.append(f'<span class="str">{chars[i:j]}</span>')
                i = j
                continue
        
        # Check for f-string prefix
        if chars[i] == 'f' and i + 1 < n and chars[i+1] in ('"', "'"):
            quote = chars[i+1]
            j = i + 2
            while j < n and chars[j] != quote:
                if chars[j] == '\\':
                    j += 2
                else:
                    j += 1
            if j < n:
                j += 1
            result.append(f'<span class="str">{chars[i:j]}</span>')
            i = j
            continue
        
        # Check for words (identifiers/keywords)
        if chars[i].isalpha() or chars[i] == '_':
            j = i
            while j < n and (chars[j].isalnum() or chars[j] == '_'):
                j += 1
            word = chars[i:j]
            
            CONTROL = {'if', 'else', 'elif', 'for', 'while', 'return', 'break',
                       'continue', 'try', 'except', 'finally', 'raise', 'with',
                       'as', 'yield', 'await', 'assert'}
            DECL = {'def', 'class', 'import', 'from', 'lambda', 'global',
                    'nonlocal', 'async', 'and', 'or', 'not', 'in', 'is', 'pass',
                    'del'}
            CONST = {'None', 'True', 'False'}
            SELF = {'self', 'cls'}
            BUILTIN = {'print', 'len', 'range', 'sorted', 'max', 'min', 'sum',
                       'round', 'enumerate', 'zip', 'map', 'filter', 'isinstance',
                       'type', 'super', 'open', 'abs', 'any', 'all', 'list',
                       'dict', 'set', 'tuple', 'str', 'int', 'float', 'bool',
                       'getattr', 'setattr', 'hasattr', 'property'}
            
            if word in CONTROL:
                result.append(f'<span class="kw2">{word}</span>')
            elif word in DECL:
                result.append(f'<span class="kw">{word}</span>')
            elif word in CONST:
                result.append(f'<span class="kw">{word}</span>')
            elif word in SELF:
                result.append(f'<span class="par">{word}</span>')
            elif word in BUILTIN:
                result.append(f'<span class="fn">{word}</span>')
            else:
                result.append(word)
            i = j
            continue
        
        # Check for numbers
        if chars[i].isdigit():
            j = i
            while j < n and (chars[j].isdigit() or chars[j] == '.'):
                j += 1
            result.append(f'<span class="num">{chars[i:j]}</span>')
            i = j
            continue
        
        # Check for decorator
        if chars[i] == '@':
            j = i + 1
            while j < n and (chars[j].isalnum() or chars[j] in '._'):
                j += 1
            result.append(f'<span class="dec">{chars[i:j]}</span>')
            i = j
            continue
        
        # Default: emit character as-is
        result.append(chars[i])
        i += 1
    
    return ''.join(result)


def make_vscode_html(filename: str, code: str) -> str:
    """Build VS Code macOS HTML page with proper syntax highlighting."""
    lines = code.split("\n")
    
    gutter_lines = []
    code_lines = []
    for i, line in enumerate(lines, 1):
        gutter_lines.append(str(i))
        code_lines.append(highlight_line(line))
    
    gutter = "\n".join(gutter_lines)
    code_body = "\n".join(code_lines)
    
    return f"""<!DOCTYPE html>
<html>
<head>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: #1e1e1e; font-family: 'Consolas', 'Courier New', monospace; }}
    .titlebar {{
        background: #323233;
        padding: 10px 16px;
        display: flex;
        align-items: center;
        border-bottom: 1px solid #252526;
    }}
    .traffic {{ display: flex; gap: 8px; margin-right: 16px; }}
    .dot {{ width: 12px; height: 12px; border-radius: 50%; }}
    .d-r {{ background: #ff5f57; }}
    .d-y {{ background: #febc2e; }}
    .d-g {{ background: #28c840; }}
    .tab {{
        background: #1e1e1e;
        color: #cccccc;
        padding: 5px 14px;
        font-size: 13px;
        font-family: -apple-system, 'Segoe UI', sans-serif;
        border-radius: 6px 6px 0 0;
        border: 1px solid #3c3c3c;
        border-bottom: none;
    }}
    .editor {{ display: flex; }}
    .gutter {{
        background: #1e1e1e;
        color: #858585;
        text-align: right;
        padding: 10px 10px 10px 14px;
        font-size: 13px;
        line-height: 1.5;
        user-select: none;
        border-right: 1px solid #2d2d2d;
        white-space: pre;
    }}
    .code {{
        background: #1e1e1e;
        color: #d4d4d4;
        padding: 10px 14px;
        font-size: 13px;
        line-height: 1.5;
        white-space: pre;
        flex: 1;
    }}
    .kw  {{ color: #569cd6; }}
    .kw2 {{ color: #c586c0; }}
    .str {{ color: #ce9178; }}
    .cmt {{ color: #6a9955; font-style: italic; }}
    .num {{ color: #b5cea8; }}
    .dec {{ color: #dcdcaa; }}
    .fn  {{ color: #dcdcaa; }}
    .par {{ color: #9cdcfe; }}
</style>
</head>
<body>
    <div class="titlebar">
        <div class="traffic">
            <div class="dot d-r"></div>
            <div class="dot d-y"></div>
            <div class="dot d-g"></div>
        </div>
        <div class="tab">{html_mod.escape(filename)}</div>
    </div>
    <div class="editor">
        <div class="gutter">{gutter}</div>
        <div class="code">{code_body}</div>
    </div>
</body>
</html>"""


# ── BODY SNIPPETS ────────────────────────────────────────────────────
SNIPPETS = {
    "snippet_robots_check": ("robots_check.py", '''def is_allowed(url: str, user_agent: str) -> bool:
    rp = _get_parser(url)
    return rp.can_fetch(user_agent, url)


def crawl_delay(url: str, user_agent: str,
                default_seconds: float) -> float:
    rp = _get_parser(url)
    delay = rp.crawl_delay(user_agent)
    if delay is None:
        return default_seconds
    return max(float(delay), default_seconds)'''),

    "snippet_polite_get": ("http_client.py", '''def polite_get(url, timeout=15, max_retries=3):
    if not is_allowed(url, settings.CRAWLER_USER_AGENT):
        raise RobotsDisallowed(
            f"robots.txt disallows: {url}")
    host = urlparse(url).netloc
    delay = crawl_delay(url,
        settings.CRAWLER_USER_AGENT,
        settings.CRAWL_DELAY_SECONDS)
    last = _last_request_time.get(host, 0.0)
    wait = delay - (time.monotonic() - last)
    if wait > 0:
        time.sleep(wait)  # Enforce crawl-delay'''),

    "snippet_preprocessing": ("text_preprocessing.py", '''def preprocess(text: str) -> str:
    text = clean_text(text)
    text = to_lowercase(text)
    tokens = tokenise(text)
    tokens = remove_stopwords(tokens)
    tokens = stem_tokens(tokens)
    return " ".join(tokens)'''),

    "snippet_build_index": ("vector_space_model.py", '''class VectorSpaceSearchEngine:
    def build_index(self) -> int:
        docs = list(
            research_outputs_col().find({}))
        corpus = [preprocess(d.get("content", ""))
                  for d in docs]
        vectorizer = TfidfVectorizer()
        matrix = vectorizer.fit_transform(corpus)
        self._vectorizer = vectorizer
        self._doc_matrix = matrix
        self._documents = docs
        return len(docs)'''),

    "snippet_search": ("vector_space_model.py", '''def search(self, query, page=1, limit=10):
    query_clean = preprocess(query)
    query_vec = self._vectorizer.transform(
        [query_clean])
    sims = cosine_similarity(
        query_vec, self._doc_matrix).flatten()
    ranked = np.argsort(-sims)
    results = [(i, float(sims[i]))
               for i in ranked
               if sims[i] > 0.0]'''),

    "snippet_dataset": ("build_dataset.py", '''TARGET_DOCS_PER_CATEGORY = 180

def select_top_n(docs, n):
    """Prefer longer documents."""
    return sorted(
        docs,
        key=lambda d: d["word_count"],
        reverse=True)[:n]'''),
}

# ── APPENDIX: FULL CODE FILES ────────────────────────────────────────
CODE_FILES = [
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
    ("task2_clustering_kmeans", "task2_document_clustering/backend/clustering/kmeans_model.py"),
    ("task2_preprocessing", "task2_document_clustering/backend/preprocessing/text_preprocessing.py"),
    ("task2_routes_api", "task2_document_clustering/backend/routes/api.py"),
    ("task2_database_mongo", "task2_document_clustering/backend/database/mongo_client.py"),
    ("task2_config_settings", "task2_document_clustering/backend/config/settings.py"),
    ("task2_visualization_pca", "task2_document_clustering/backend/visualization/pca_plot.py"),
    ("task2_run", "task2_document_clustering/backend/run.py"),
    ("task2_scripts_build_dataset", "task2_document_clustering/scripts/build_dataset.py"),
    ("task2_scripts_train_model", "task2_document_clustering/scripts/train_model.py"),
    ("frontend_app", "unified_frontend/app.py"),
    ("frontend_js", "unified_frontend/static/js/app.js"),
    ("frontend_css", "unified_frontend/static/css/style.css"),
    ("frontend_html", "unified_frontend/templates/index.html"),
]


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # ── 1. Body snippets ──
        print("=== Body Snippets ===")
        for name, (title, code) in SNIPPETS.items():
            html = make_vscode_html(title, code)
            temp = SNIPPETS_DIR / "_t.html"
            temp.write_text(html, encoding="utf-8")
            lines = len(code.split("\n"))
            h = lines * 21 + 50
            page = await browser.new_page(viewport={"width": 700, "height": h})
            await page.goto(f"file:///{temp.resolve()}")
            await page.wait_for_timeout(200)
            await page.screenshot(path=str(SNIPPETS_DIR / f"{name}.png"))
            await page.close()
            temp.unlink()
            print(f"  {name}.png")

        # ── 2. Appendix full code ──
        print("\n=== Appendix Code ===")
        for name, rel_path in CODE_FILES:
            full_path = PROJECT_ROOT / rel_path
            if not full_path.exists():
                print(f"  SKIP: {rel_path}")
                continue

            code = full_path.read_text(encoding="utf-8", errors="replace")
            fname = Path(rel_path).name
            all_lines = code.split("\n")
            total_lines = len(all_lines)

            if total_lines <= MAX_LINES_PER_PART:
                # Single screenshot
                html = make_vscode_html(fname, code)
                temp = CODE_DIR / "_t.html"
                temp.write_text(html, encoding="utf-8")
                h = total_lines * 21 + 50
                page = await browser.new_page(viewport={"width": 900, "height": h})
                await page.goto(f"file:///{temp.resolve()}")
                await page.wait_for_timeout(200)
                await page.screenshot(path=str(CODE_DIR / f"{name}.png"), full_page=True)
                await page.close()
                temp.unlink()
                print(f"  {name}.png ({total_lines} lines)")
            else:
                # Split into parts
                part_num = 0
                for start in range(0, total_lines, MAX_LINES_PER_PART):
                    part_num += 1
                    chunk_lines = all_lines[start:start + MAX_LINES_PER_PART]
                    chunk_code = "\n".join(chunk_lines)
                    
                    # Re-number lines starting from actual line number
                    highlighted_lines = []
                    gutter_lines = []
                    for j, line in enumerate(chunk_lines):
                        line_num = start + j + 1
                        gutter_lines.append(str(line_num))
                        highlighted_lines.append(highlight_line(line))
                    
                    gutter = "\n".join(gutter_lines)
                    code_body = "\n".join(highlighted_lines)
                    
                    part_title = f"{fname} (Part {part_num})"
                    # Build HTML manually with correct line numbers
                    part_html = make_vscode_html(part_title, "placeholder")
                    # Replace placeholder with actual content
                    # Easier: just build the html directly
                    part_html = f"""<!DOCTYPE html>
<html><head><style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#1e1e1e; font-family:'Consolas','Courier New',monospace; }}
.titlebar {{ background:#323233; padding:10px 16px; display:flex; align-items:center; border-bottom:1px solid #252526; }}
.traffic {{ display:flex; gap:8px; margin-right:16px; }}
.dot {{ width:12px; height:12px; border-radius:50%; }}
.d-r {{ background:#ff5f57; }} .d-y {{ background:#febc2e; }} .d-g {{ background:#28c840; }}
.tab {{ background:#1e1e1e; color:#ccc; padding:5px 14px; font-size:13px; font-family:-apple-system,sans-serif; border-radius:6px 6px 0 0; border:1px solid #3c3c3c; border-bottom:none; }}
.editor {{ display:flex; }}
.gutter {{ background:#1e1e1e; color:#858585; text-align:right; padding:10px 10px 10px 14px; font-size:13px; line-height:1.5; user-select:none; border-right:1px solid #2d2d2d; white-space:pre; }}
.code {{ background:#1e1e1e; color:#d4d4d4; padding:10px 14px; font-size:13px; line-height:1.5; white-space:pre; flex:1; }}
.kw {{ color:#569cd6; }} .kw2 {{ color:#c586c0; }} .str {{ color:#ce9178; }}
.cmt {{ color:#6a9955; font-style:italic; }} .num {{ color:#b5cea8; }}
.dec {{ color:#dcdcaa; }} .fn {{ color:#dcdcaa; }} .par {{ color:#9cdcfe; }}
</style></head><body>
<div class="titlebar"><div class="traffic"><div class="dot d-r"></div><div class="dot d-y"></div><div class="dot d-g"></div></div><div class="tab">{html_mod.escape(part_title)}</div></div>
<div class="editor"><div class="gutter">{gutter}</div><div class="code">{code_body}</div></div>
</body></html>"""
                    
                    temp = CODE_DIR / "_t.html"
                    temp.write_text(part_html, encoding="utf-8")
                    h = len(chunk_lines) * 21 + 50
                    page = await browser.new_page(viewport={"width": 900, "height": h})
                    await page.goto(f"file:///{temp.resolve()}")
                    await page.wait_for_timeout(200)
                    out_name = f"{name}_part{part_num}.png"
                    await page.screenshot(path=str(CODE_DIR / out_name), full_page=True)
                    await page.close()
                    temp.unlink()
                    print(f"  {out_name} (lines {start+1}-{start+len(chunk_lines)})")

        await browser.close()
    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
