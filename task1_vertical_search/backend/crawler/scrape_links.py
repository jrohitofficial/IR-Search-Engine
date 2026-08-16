import os
import time
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

def scrape_links():
    urls = [
        "https://pureportal.coventry.ac.uk/en/organisations/centre-for-healthcare-and-community-transformation/publications/?page=0",
        "https://pureportal.coventry.ac.uk/en/organisations/centre-for-healthcare-and-community-transformation/publications/?page=1",
        "https://pureportal.coventry.ac.uk/en/organisations/centre-for-healthcare-and-community-transformation/persons/?page=0",
        "https://pureportal.coventry.ac.uk/en/organisations/centre-for-healthcare-and-community-transformation/persons/?page=1",
        "https://pureportal.coventry.ac.uk/en/organisations/centre-for-healthcare-and-community-transformation/persons/?page=2",
    ]

    all_links = set()

    print("Launching Undetected Chromedriver...")
    options = uc.ChromeOptions()
    try:
        driver = uc.Chrome(options=options, version_main=151)
    except:
        try:
            driver = uc.Chrome(options=options, version_main=152)
        except:
            driver = uc.Chrome(options=options)

    for i, url in enumerate(urls):
        print(f"Fetching: {url}")
        driver.get(url)
        
        # Match user's logic exactly: sleep 10 on first, 5 on subsequent
        if i == 0:
            time.sleep(10)
        else:
            time.sleep(5)
            
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Get all links
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "pureportal.coventry.ac.uk/en/publications/" in href or "pureportal.coventry.ac.uk/en/persons/" in href:
                clean_link = href.split("#")[0].split("?")[0]
                all_links.add(clean_link)
                
        print(f"Total relevant links gathered so far: {len(all_links)}")

    driver.quit()

    links_file = os.path.join(os.path.dirname(__file__), "links.txt")
    with open(links_file, "w") as f:
        for link in all_links:
            f.write(link + "\n")

    print(f"\nSuccess! Saved {len(all_links)} links to links.txt")

if __name__ == "__main__":
    scrape_links()
