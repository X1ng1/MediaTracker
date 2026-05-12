import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import json
import os
from mangadex import fetch_updates_api
from webtoon import fetch_updates_webtoon

with open("sites.json", "r", encoding="utf-8") as f:
    SITES = json.load(f)

with open("followed_titles.json", "r", encoding="utf-8") as f:
    FOLLOWED_TITLES = json.load(f)

DATA_FILE = "updates.json"

def fetch_updates(config):
    scraper = cloudscraper.create_scraper()
    res = scraper.get(config["url"])
    soup = BeautifulSoup(res.text, "html.parser")

    # Find container for latest releases
    # Header names will differ for each website, so can't use hardcoded section names
    if "section_header" in config:
        header = soup.find(lambda tag: tag.name in ("h1", "h2", "h3") and config["section_header"] in tag.get_text())
        if not header:
            print(f"Could not find section header: {config['section_header']}")
            return []
        container = header.find_next(config["container"])
    else:
        container = soup.select_one(config["container"])

    if not container:
        return []

    cards = container.select(config["card"])
    results = []

    for card in cards:
        # Title
        title_el = card.select_one(config["title"])
        if not title_el:
            continue

        # Latest chapter and time (optional)
        chapter_el = card.select_one(config["chapter"]) if config.get("chapter") else None
        time_el = card.select_one(config["time"]) if config.get("time") else None

        time_raw = time_el.text.strip() if time_el else ""
        time_val = time_raw or (time_el.get("datetime", "") if time_el else "")

        link_el = card.select_one(config["link"]) if config.get("link") else card.select_one("a")
        link = link_el.get("href", "") if link_el else ""

        results.append({
            "title": title_el.text.strip(),
            "chapter": chapter_el.text.strip() if chapter_el else "",
            "time": time_val,
            "link": link
        })

    return results

def load_updates():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        return json.loads(content) if content else {}

def save_updates(new_items, site_name):
    existing = load_updates()
    for item in new_items:
        existing[item["title"]] = {
            "chapter": item["chapter"],
            "time": item["time"],
            "site": site_name,
            "link": item.get("link", "")
        }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

def is_within_24_hours(time_str):
    if not time_str:
        return True

    time_str = time_str.lower().strip()
    now = datetime.now(timezone.utc)

    # Relative timestamps (always recent)
    if any(unit in time_str for unit in [
        "second", "seconds",
        "minute", "minutes", "min", "mins",
        "hour", "hours"
    ]):
        return True
    if "today" in time_str:
        return True
    if "yesterday" in time_str:
        return True
    
    dt = None
    # ISO format
    try:
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
    except ValueError:
        pass
    # May-08-2026
    if dt is None:
        try:
            dt = datetime.strptime(time_str, "%b-%d-%Y")
            dt = dt.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    # May 8, 2026
    if dt is None:
        try:
            dt = datetime.strptime(time_str, "%b %d, %Y")
            dt = dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return True 
    if dt is None:
        return True
    return (now - dt) <= timedelta(hours=24)

def main():
    for site_name, config in SITES.items():
        print(f"\nScraping {site_name}...")
        
        if config.get("type") == "api":
            data = fetch_updates_api(config)
        elif config.get("type") == "webtoon":
            data = fetch_updates_webtoon(config)
        else:
            data = fetch_updates(config)
        # Only want titles that user is following
        todays = [item for item in data if is_within_24_hours(item["time"]) and item["title"] in FOLLOWED_TITLES]

        if todays:
            print(f"Releases today:")
            for item in todays:
                print(f"  {item['title']} — {item['chapter']} ({item['time']})")
            save_updates(todays, site_name)
        else:
            print("No releases today.")

if __name__ == "__main__":
    main()