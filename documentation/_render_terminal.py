"""
Renders real captured text (crawl logs, pytest output, script output) into
a clean, readable "terminal window" PNG for the evidence document. The
chrome (rounded window, traffic-light dots) is decorative only -- every
character of text rendered is copied verbatim from real command output,
nothing here is invented.
"""
import html
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

FIGDIR = Path(__file__).parent / "figures"
FIGDIR.mkdir(exist_ok=True)

TEMPLATE = """<!DOCTYPE html><html><head><meta charset="utf-8"><style>
  body{{margin:0;background:#0d1117;font-family:-apple-system,Segoe UI,sans-serif;}}
  .win{{width:{width}px;border-radius:12px;overflow:hidden;box-shadow:0 20px 45px rgba(0,0,0,.5);border:1px solid #2a2f3a;}}
  .bar{{background:#161b22;padding:10px 14px;display:flex;align-items:center;gap:8px;border-bottom:1px solid #2a2f3a;}}
  .dot{{width:11px;height:11px;border-radius:50%;}}
  .r{{background:#ff5f57;}} .y{{background:#febc2e;}} .g{{background:#28c840;}}
  .title{{margin-left:10px;color:#8b949e;font-size:12.5px;}}
  pre{{margin:0;padding:18px 22px;color:#c9d1d9;font-family:Consolas,"Cascadia Mono",monospace;
       font-size:13.2px;line-height:1.55;white-space:pre-wrap;word-break:break-word;}}
  .ok{{color:#3fb950;}} .warn{{color:#d29922;}} .err{{color:#f85149;}} .info{{color:#58a6ff;}} .dim{{color:#6e7681;}}
</style></head><body><div class="win"><div class="bar"><span class="dot r"></span><span class="dot y"></span><span class="dot g"></span><span class="title">{title}</span></div><pre>{body}</pre></div></body></html>"""


def colourise(line: str) -> str:
    esc = html.escape(line)
    if " ERROR " in line or line.strip().startswith("FAILED") or "Traceback" in line:
        return f'<span class="err">{esc}</span>'
    if " WARNING " in line:
        return f'<span class="warn">{esc}</span>'
    if "PASSED" in line or "PASS" in line or " passed" in line or "inserted" in line:
        return f'<span class="ok">{esc}</span>'
    if " INFO " in line:
        return f'<span class="info">{esc}</span>'
    return esc


def render(text: str, title: str, out_name: str, width: int = 1180):
    lines = text.rstrip("\n").split("\n")
    body = "\n".join(colourise(l) for l in lines)
    html_doc = TEMPLATE.format(width=width, title=html.escape(title), body=body)
    tmp = FIGDIR / "_tmp_terminal.html"
    tmp.write_text(html_doc, encoding="utf-8")

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument(f"--window-size={width + 40},2600")
    driver = webdriver.Chrome(options=opts)
    try:
        driver.get(tmp.as_uri())
        time.sleep(0.4)
        el = driver.find_element("css selector", ".win")
        height = driver.execute_script("return arguments[0].scrollHeight", el) + 40
        driver.set_window_size(width + 40, min(height, 5000))
        time.sleep(0.2)
        el = driver.find_element("css selector", ".win")
        el.screenshot(str(FIGDIR / out_name))
        print("saved", out_name)
    finally:
        driver.quit()
        tmp.unlink(missing_ok=True)
