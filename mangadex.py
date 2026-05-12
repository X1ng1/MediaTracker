import cloudscraper

# MangaDex is a JS app and cloudscraper gets the raw HTML b4 JS renders
# Use MangaDex's public API instead of scraping HTML
def fetch_updates_api(config):
    scraper = cloudscraper.create_scraper()
    res = scraper.get(config["url"])
    data = res.json()

    results = []
    for item in data.get("data", []):
        attrs = item.get("attributes", {})
        chapter = attrs.get("chapter", "")
        publish_at = attrs.get("publishAt", "")

        manga_title = None
        for rel in item.get("relationships", []):
            if rel.get("type") == "manga":
                titles = rel.get("attributes", {}).get("title", {})
                manga_title = titles.get("en") or next(iter(titles.values()), None)
                break

        if not manga_title or not chapter:
            continue
        # print(manga_title)

        chapter_id = item.get("id", "")
        results.append({
            "title": manga_title,
            "chapter": f"Chapter {chapter}",
            "time": publish_at,
            "link": f"https://mangadex.org/chapter/{chapter_id}" if chapter_id else ""
        })

    return results
