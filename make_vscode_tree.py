import asyncio
from playwright.async_api import async_playwright
import os

html = '''<!DOCTYPE html>
<html>
<head>
<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
body { background: #1e1e1e; color: #cccccc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 13px; margin: 0; padding: 10px; width: 350px; }
.r { display: flex; align-items: center; padding: 2px 0; user-select: none; margin-left: -5px; }
.r:hover { background: #2a2d2e; }
.i { width: 14px; height: 100%; display: inline-block; border-left: 1px solid #404040; margin-left: 10px; padding-left: 4px; }
.ic { width: 16px; height: 16px; margin-right: 6px; font-size: 14px; text-align: center; }
.chev { font-size: 10px; margin-right: 2px; margin-left: 5px; color: #c5c5c5; display: inline-block; width: 12px; text-align: center; font-weight: bold; font-family: monospace; }
.fld { color: #dcb67a; }
.py { color: #3572A5; }
.env { color: #fada5e; }
.htm { color: #e34c26; }
.css { color: #563d7c; }
.js { color: #f0db4f; }
.yml { color: #cb171e; }
.md { color: #4aa5f0; }
.txt { color: #cccccc; }
</style>
</head>
<body>
'''

tree = [
    (0, 'folder_open', 'IR_COURSEWORK'),
    (1, 'folder_open', 'task1_vertical_search'),
    (2, 'folder_open', 'backend'),
    (3, 'folder', 'api'),
    (3, 'folder', 'config'),
    (3, 'folder', 'crawler'),
    (3, 'folder', 'database'),
    (3, 'file_py', 'run.py'),
    (2, 'folder', 'tests'),
    (1, 'folder_open', 'task2_document_clustering'),
    (2, 'folder_open', 'backend'),
    (3, 'folder', 'clustering'),
    (3, 'folder', 'config'),
    (3, 'folder', 'database'),
    (3, 'folder', 'routes'),
    (3, 'file_py', 'run.py'),
    (2, 'folder_open', 'scripts'),
    (3, 'file_py', 'build_dataset.py'),
    (3, 'file_py', 'train_model.py'),
    (1, 'folder_open', 'unified_frontend'),
    (2, 'folder_open', 'static'),
    (3, 'folder', 'css'),
    (3, 'folder', 'js'),
    (2, 'folder', 'templates'),
    (2, 'file_py', 'app.py'),
    (1, 'file_env', '.env'),
    (1, 'file_env', '.env.example'),
    (1, 'file_txt', '.gitignore'),
    (1, 'file_md', 'README.md'),
    (1, 'file_yml', 'render.yaml')
]

for level, type_, name in tree:
    indents = "<div class='i'></div>" * level
    
    if 'folder' in type_:
        chev = "v" if type_ == 'folder_open' else ">"
        icon = "<i class='ic fld fas fa-folder'></i>" if type_ == 'folder' else "<i class='ic fld fas fa-folder-open'></i>"
    else:
        chev = "<div style='width: 16px; display: inline-block;'></div>"
        if type_ == 'file_py': icon = "<i class='ic py fab fa-python'></i>"
        elif type_ == 'file_env': icon = "<i class='ic env fas fa-cog'></i>"
        elif type_ == 'file_html': icon = "<i class='ic htm fab fa-html5'></i>"
        elif type_ == 'file_css': icon = "<i class='ic css fab fa-css3-alt'></i>"
        elif type_ == 'file_js': icon = "<i class='ic js fab fa-js'></i>"
        elif type_ == 'file_md': icon = "<i class='ic md fab fa-markdown'></i>"
        elif type_ == 'file_yml': icon = "<i class='ic yml fas fa-wrench'></i>"
        else: icon = "<i class='ic txt fas fa-file-alt'></i>"
        
    chev_div = f"<div class='chev'>{chev}</div>" if 'folder' in type_ else chev
    
    html += f"<div class='r'>{indents}{chev_div}{icon}{name}</div>\n"

html += "</body></html>"
with open('vscode_tree.html', 'w', encoding='utf-8') as f:
    f.write(html)

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 350, "height": 780})
        # Use an absolute URL using pathlib
        from pathlib import Path
        uri = Path('vscode_tree.html').resolve().as_uri()
        await page.goto(uri)
        await page.wait_for_timeout(3000) # wait for fontawesome to load
        await page.locator("body").screenshot(path="documentation/screenshots/snippets/snippet_tree.png")
        await browser.close()

asyncio.run(capture())
