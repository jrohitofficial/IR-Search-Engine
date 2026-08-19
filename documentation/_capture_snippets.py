"""
Generate VS Code-style syntax-highlighted code snippet screenshots
for use in the document body.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

SCREENSHOTS_DIR = Path(__file__).resolve().parent / "screenshots" / "snippets"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Python keyword highlighting
PYTHON_KEYWORDS = {
    'def', 'class', 'return', 'if', 'else', 'elif', 'for', 'while', 'in',
    'not', 'and', 'or', 'is', 'None', 'True', 'False', 'from', 'import',
    'raise', 'try', 'except', 'with', 'as', 'self', 'lambda', 'yield',
    'break', 'continue', 'pass', 'global', 'async', 'await',
}

def syntax_highlight(code: str) -> str:
    """Simple Python syntax highlighter producing HTML spans."""
    import re
    # Escape HTML first
    code = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    # Comments
    code = re.sub(r'(#.*?)$', r'<span class="comment">\1</span>', code, flags=re.MULTILINE)
    
    # Strings (double and single quoted)
    code = re.sub(r'(\"\"\".*?\"\"\")', r'<span class="string">\1</span>', code, flags=re.DOTALL)
    code = re.sub(r'(f?\"[^\"]*?\")', r'<span class="string">\1</span>', code)
    code = re.sub(r"(f?\'[^\']*?\')", r'<span class="string">\1</span>', code)
    
    # Decorators
    code = re.sub(r'(@\w+[\.\w]*)', r'<span class="decorator">\1</span>', code)
    
    # Keywords
    for kw in PYTHON_KEYWORDS:
        code = re.sub(rf'\b({kw})\b', rf'<span class="keyword">\1</span>', code)
    
    # Numbers
    code = re.sub(r'\b(\d+\.?\d*)\b', r'<span class="number">\1</span>', code)
    
    # Built-in functions
    for fn in ['print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict', 'set', 'max', 'min', 'sum', 'round', 'type']:
        code = re.sub(rf'\b({fn})\b(?=\()', rf'<span class="builtin">\1</span>', code)
    
    return code


def generate_snippet_html(title: str, code: str) -> str:
    highlighted = syntax_highlight(code)
    
    # Add line numbers
    lines = highlighted.split("\n")
    numbered = []
    for i, line in enumerate(lines, 1):
        numbered.append(f'<span class="ln">{i:>3}</span>  {line}')
    body = "\n".join(numbered)
    
    return f"""<!DOCTYPE html>
<html>
<head>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        background: #1e1e1e;
        padding: 0;
        font-family: 'Consolas', 'Courier New', monospace;
    }}
    .titlebar {{
        background: #323233;
        color: #cccccc;
        padding: 7px 16px;
        font-size: 12px;
        font-family: 'Segoe UI', 'Helvetica', sans-serif;
        border-bottom: 1px solid #252526;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .dot {{ width: 12px; height: 12px; border-radius: 50%; display: inline-block; }}
    .dot-red {{ background: #ff5f56; }}
    .dot-yellow {{ background: #ffbd2e; }}
    .dot-green {{ background: #27c93f; }}
    .filename {{ margin-left: 12px; }}
    pre {{
        color: #d4d4d4;
        font-size: 13px;
        line-height: 1.6;
        padding: 12px 16px;
        overflow: visible;
        white-space: pre;
    }}
    .ln {{ color: #858585; user-select: none; }}
    .keyword {{ color: #569cd6; }}
    .string {{ color: #ce9178; }}
    .comment {{ color: #6a9955; font-style: italic; }}
    .number {{ color: #b5cea8; }}
    .decorator {{ color: #dcdcaa; }}
    .builtin {{ color: #dcdcaa; }}
</style>
</head>
<body>
    <div class="titlebar">
        <span class="dot dot-red"></span>
        <span class="dot dot-yellow"></span>
        <span class="dot dot-green"></span>
        <span class="filename">{title}</span>
    </div>
    <pre>{body}</pre>
</body>
</html>"""


# All code snippets used in the document body
SNIPPETS = {
    "snippet_robots_check": {
        "title": "crawler/robots_check.py",
        "code": '''def is_allowed(url: str, user_agent: str) -> bool:
    rp = _get_parser(url)
    return rp.can_fetch(user_agent, url)


def crawl_delay(url: str, user_agent: str, default_seconds: float) -> float:
    rp = _get_parser(url)
    delay = rp.crawl_delay(user_agent)
    if delay is None:
        return default_seconds
    return max(float(delay), default_seconds)'''
    },
    "snippet_polite_get": {
        "title": "crawler/http_client.py — polite_get()",
        "code": '''def polite_get(url: str, timeout: int = 15, max_retries: int = 3) -> str:
    if not is_allowed(url, settings.CRAWLER_USER_AGENT):
        raise RobotsDisallowed(f"robots.txt disallows crawling: {url}")

    host = urlparse(url).netloc
    delay = crawl_delay(url, settings.CRAWLER_USER_AGENT, settings.CRAWL_DELAY_SECONDS)
    last = _last_request_time.get(host, 0.0)
    wait = delay - (time.monotonic() - last)
    if wait > 0:
        time.sleep(wait)  # Enforce crawl-delay'''
    },
    "snippet_preprocessing": {
        "title": "preprocessing/text_preprocessing.py",
        "code": '''def preprocess(text: str) -> str:
    text = clean_text(text)
    text = to_lowercase(text)
    tokens = tokenise(text)
    tokens = remove_stopwords(tokens)
    tokens = stem_tokens(tokens)
    return " ".join(tokens)'''
    },
    "snippet_build_index": {
        "title": "ranking/vector_space_model.py — build_index()",
        "code": '''class VectorSpaceSearchEngine:
    def build_index(self) -> int:
        docs = list(research_outputs_col().find({}))
        corpus = [preprocess(d.get("content", "")) for d in docs]
        vectorizer = TfidfVectorizer()
        matrix = vectorizer.fit_transform(corpus)
        self._vectorizer = vectorizer
        self._doc_matrix = matrix
        self._documents = docs
        return len(docs)'''
    },
    "snippet_search": {
        "title": "ranking/vector_space_model.py — search()",
        "code": '''def search(self, query: str, page: int = 1, limit: int = 10) -> dict:
    query_clean = preprocess(query)
    query_vector = self._vectorizer.transform([query_clean])
    similarities = cosine_similarity(query_vector, self._doc_matrix).flatten()
    ranked_indices = np.argsort(-similarities)
    ranked = [(idx, float(similarities[idx]))
              for idx in ranked_indices if similarities[idx] > 0.0]'''
    },
    "snippet_dataset": {
        "title": "scripts/build_dataset.py — select_top_n()",
        "code": '''TARGET_DOCS_PER_CATEGORY = 180  # Exceeds minimum requirement of 150

def select_top_n(docs: list[dict], n: int) -> list[dict]:
    """Prefer longer, information-richer documents."""
    return sorted(docs, key=lambda d: d["word_count"], reverse=True)[:n]'''
    },
}


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        for name, data in SNIPPETS.items():
            html = generate_snippet_html(data["title"], data["code"])
            
            temp_file = SCREENSHOTS_DIR / f"_temp_{name}.html"
            temp_file.write_text(html, encoding="utf-8")
            
            # Calculate height based on lines
            line_count = len(data["code"].split("\n"))
            height = line_count * 22 + 50
            
            page = await browser.new_page(viewport={"width": 800, "height": height})
            await page.goto(f"file:///{temp_file.resolve()}")
            await page.wait_for_timeout(300)
            
            out_path = SCREENSHOTS_DIR / f"{name}.png"
            await page.screenshot(path=str(out_path))
            await page.close()
            temp_file.unlink()
            print(f"  OK: {name}.png")
        
        await browser.close()
    print(f"\nAll snippets saved to {SCREENSHOTS_DIR}")

if __name__ == "__main__":
    asyncio.run(main())
