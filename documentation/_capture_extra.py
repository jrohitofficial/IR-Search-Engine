import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

OUT = Path(__file__).parent / "screenshots"

opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--window-size=1480,1400")
driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 15)

try:
    driver.get("http://localhost:5003/")
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.tab-btn[data-tab="cluster"]'))).click()
    time.sleep(1.0)
    driver.find_element(By.CSS_SELECTOR, '.stats-tab[data-stats="model"]').click()
    time.sleep(0.8)
    el = driver.find_element(By.CSS_SELECTOR, ".stats-card")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", el)
    time.sleep(0.5)
    driver.save_screenshot(str(OUT / "08_unified_model_evaluation.png"))
    print("saved 08")

    fig = driver.find_element(By.ID, "cluster-figure")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'})", fig)
    time.sleep(1.2)
    driver.save_screenshot(str(OUT / "09_unified_figure_card.png"))
    print("saved 09, figure natural size:", driver.execute_script(
        "return [arguments[0].naturalWidth, arguments[0].naturalHeight]", fig))
finally:
    driver.quit()
