# MediaTracker

Keeping track of new manga chapters, webtoon episodes, or other content releases often requires users to manually visit multiple websites and repeatedly check for updates. This process is time-consuming, inefficient, and makes it easy to miss new releases.

MediaTracker solves that problem by automating update tracking across multiple sources. It scrapes selected websites, detects newly released content, and extracts relevant information.

---

## Local Deployment

1. **Install dependencies:**
`pip install -r requirements.txt`
2. **Create a file named "followed_titles.json"**
3. **Add manga titles to followed_titles.json. An example is:**
```
[
    "Pure Love Operation",
    "Yu-Gi-Oh! OCG Structures",
    "Campfire Friends",
    "Omniscient Reader's Viewpoint",
    "BUNGO-unreal-"
]
```
4. **Run the program:**
`python index.py`

---
