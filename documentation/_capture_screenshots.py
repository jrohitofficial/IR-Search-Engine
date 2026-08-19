import asyncio
import time
import os
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "http://127.0.0.1:5003"
SCREENSHOTS_DIR = Path(__file__).resolve().parent / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)

async def capture_ui():
    print("Starting Playwright...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        print(f"Navigating to {BASE_URL}...")
        await page.goto(BASE_URL)
        await page.wait_for_load_state("networkidle")
        
        # 1. Home / Search
        print("Taking Home screenshot...")
        await page.screenshot(path=str(SCREENSHOTS_DIR / "new_01_search_home.png"))
        
        # 2. Search for "mental health"
        print("Searching for 'mental health'...")
        await page.fill("#search-input", "mental health")
        await page.click("button[type='submit']")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=str(SCREENSHOTS_DIR / "02_task1_search_mental_health.png"))
        
        # 3. Crawler Status
        print("Taking Crawler Status screenshot...")
        await page.click("#crawler-status-toggle")
        await page.wait_for_timeout(500)
        await page.screenshot(path=str(SCREENSHOTS_DIR / "01_task1_crawler_status.png"))
        await page.click("#crawler-status-toggle") # hide it
        await page.wait_for_timeout(500)

        # 4. Task 2 Clustering Tab
        print("Switching to Task 2...")
        await page.click("button[data-tab='cluster']")
        await page.wait_for_timeout(1000)
        
        # 5. Help Modal
        print("Opening Help Modal...")
        await page.click("#help-btn")
        await page.wait_for_timeout(500)
        await page.screenshot(path=str(SCREENSHOTS_DIR / "new_04_help_modal.png"))
        await page.click("#close-help-btn")
        await page.wait_for_timeout(500)
        
        # 6. High Confidence Classification
        print("Testing Classification...")
        test_text = "The Labour party has announced a new election plan to increase public tax."
        await page.fill("#text-input", test_text)
        await page.click("#classify-btn")
        await page.wait_for_timeout(1500) # wait for API
        await page.screenshot(path=str(SCREENSHOTS_DIR / "06_task2_classification_results.png"))

        # 7. Data Bias Test
        print("Testing Data Bias (President)...")
        await page.click("#clear-btn")
        await page.fill("#text-input", "Donald Trump is president of India")
        await page.click("#classify-btn")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=str(SCREENSHOTS_DIR / "new_05_data_bias.png"))
        
        # 8. Prediction History
        print("Scrolling to History...")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(500)
        await page.screenshot(path=str(SCREENSHOTS_DIR / "new_06_prediction_history.png"))
        
        await browser.close()
        print("Browser automated successfully!")

if __name__ == "__main__":
    asyncio.run(capture_ui())
