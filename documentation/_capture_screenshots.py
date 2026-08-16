"""
Drives the real, running unified frontend with headless Chrome and saves
real screenshots for the evidence document. All three backends
(task1:5001, task2:5002, unified_frontend:5000) must already be running.
"""
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

OUT = Path(__file__).parent / "screenshots"
OUT.mkdir(exist_ok=True)

opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--window-size=1920,1080")
opts.add_argument("--force-device-scale-factor=0.9")
driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 15)

def shot(name):
    driver.save_screenshot(str(OUT / name))
    print("saved", name)

try:
    # 1. Home page (matches Image 2)
    driver.get("http://localhost:5003/")
    wait.until(EC.presence_of_element_located((By.ID, "search-form")))
    time.sleep(1.5)
    shot("01_unified_search_home.png")

    # 2. Crawler status open on home page (matches Image 1)
    driver.find_element(By.ID, "crawler-status-toggle").click()
    time.sleep(1.0)
    shot("04_unified_crawler_status.png")
    
    # Close it back
    driver.find_element(By.ID, "crawler-status-toggle").click()
    time.sleep(0.5)

    # 3. Search suggestions (matches Image for suggest)
    box = driver.find_element(By.ID, "search-input")
    box.clear()
    box.send_keys("Gemma")
    wait.until(EC.visibility_of_element_located((By.ID, "task1-suggestions")))
    time.sleep(1.0)
    shot("08_unified_search_suggestions.png")

    # 3. Search results for "mental health" (matches Image 3)
    box = driver.find_element(By.ID, "search-input")
    box.send_keys("mental health")
    driver.find_element(By.CSS_SELECTOR, "#search-form button").click()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".result-card")))
    time.sleep(1.0)
    shot("02_unified_search_results.png")

    # 4. Pagination / scrolled results (matches Image 4)
    box = driver.find_element(By.ID, "search-input")
    box.clear()
    box.send_keys("health")
    driver.find_element(By.CSS_SELECTOR, "#search-form button").click()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".result-card")))
    time.sleep(1.0)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(0.5)
    shot("03_unified_search_pagination.png")
    driver.execute_script("window.scrollTo(0, 0)")

    # 5. Clustering home page (matches Image 5)
    driver.find_element(By.CSS_SELECTOR, '.tab-btn[data-tab="cluster"]').click()
    time.sleep(1.0)
    shot("05_unified_cluster_home.png")

    # 6. Classification result
    ta = driver.find_element(By.ID, "text-input")
    ta.send_keys("The central bank increased interest rates to control inflation.")
    driver.find_element(By.ID, "classify-btn").click()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".result-category")))
    time.sleep(1.0)
    shot("06_unified_cluster_result.png")

    # 7. Model evaluation stats
    driver.find_element(By.CSS_SELECTOR, '.stats-tab[data-stats="model"]').click()
    time.sleep(0.5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(1.0)
    shot("07_unified_cluster_stats_and_figure.png")

    print("All screenshots captured successfully.")
finally:
    driver.quit()
