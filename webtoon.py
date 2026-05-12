import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime


# Webtoon server-renders the day-specific originals page
def fetch_updates_webtoon(config):
    day = datetime.now().strftime("%A").lower()  # e.g. 'saturday'
    url = config["base_url"] + day
    scraper = cloudscraper.create_scraper()
    res = scraper.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    results = []
    for card in soup.select("a[data-title-no]"):
        title_el = card.select_one("strong.title")
        if not title_el:
            continue
        results.append({
            "title": title_el.text.strip(),
            "chapter": "",
            "time": "",
            "link": card.get("href", "")
        })
    return results
