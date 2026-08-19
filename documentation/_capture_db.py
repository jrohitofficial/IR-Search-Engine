import asyncio
import time
import os
from pathlib import Path
from pymongo import MongoClient
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

SCREENSHOTS_DIR = Path(__file__).resolve().parent / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")

def generate_html(title, collection_name, docs):
    # Mimics MongoDB Compass Dark Mode
    html = f"""
    <html>
    <head>
        <style>
            body {{ background-color: #001e2b; color: #00ed64; font-family: 'Consolas', monospace; padding: 20px; }}
            h1 {{ color: #ffffff; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }}
            h2 {{ color: #889397; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }}
            .doc {{ background-color: #012b39; padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #00ed64; }}
            .key {{ color: #9bbbdc; }}
            .string {{ color: #e1c07a; }}
            .number {{ color: #ff8a65; }}
            .boolean {{ color: #56b6c2; }}
        </style>
    </head>
    <body>
        <h1>MongoDB Compass</h1>
        <h2>Database: {title} | Collection: {collection_name}</h2>
    """
    for doc in docs:
        html += "<div class='doc'>{\n"
        for k, v in doc.items():
            k_html = f"<span class='key'>\"{k}\"</span>"
            if isinstance(v, str):
                v_html = f"<span class='string'>\"{v}\"</span>"
            elif isinstance(v, (int, float)):
                v_html = f"<span class='number'>{v}</span>"
            elif isinstance(v, bool):
                v_html = f"<span class='boolean'>{str(v).lower()}</span>"
            else:
                v_html = f"<span class='string'>\"{str(v)[:100]}...\"</span>"
            
            html += f"  {k_html}: {v_html},<br>"
        html += "}</div>\n"
    
    html += "</body></html>"
    return html

async def capture_db():
    client = MongoClient(MONGO_URI)
    
    # Task 1 DB
    db1 = client["Task_1_Vertical_Search"]
    docs1 = list(db1["research_outputs"].find().limit(3))
    html1 = generate_html("Task_1_Vertical_Search", "research_outputs", docs1)
    
    # Task 2 DB
    db2 = client["Task_2_Document_Clustering"]
    docs2 = list(db2["clustering_predictions"].find().sort("_id", -1).limit(3))
    html2 = generate_html("Task_2_Document_Clustering", "clustering_predictions", docs2)
    
    with open("temp_db1.html", "w", encoding="utf-8") as f: f.write(html1)
    with open("temp_db2.html", "w", encoding="utf-8") as f: f.write(html2)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        
        path1 = Path("temp_db1.html").resolve()
        await page.goto(f"file://{path1}")
        await page.screenshot(path=str(SCREENSHOTS_DIR / "new_db_task1.png"))
        
        path2 = Path("temp_db2.html").resolve()
        await page.goto(f"file://{path2}")
        await page.screenshot(path=str(SCREENSHOTS_DIR / "new_db_task2.png"))
        
        await browser.close()
        
    os.remove("temp_db1.html")
    os.remove("temp_db2.html")
    print("Database screenshots captured!")

if __name__ == "__main__":
    asyncio.run(capture_db())
