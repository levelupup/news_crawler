"""
Nikkei Asia Technology News scraper.

Nikkei Asia's tech page returns 200 and embeds article data in __NEXT_DATA__.
This script parses that JSON directly — no Playwright or CAPTCHA bypass needed.
Falls back to scraping both /business/tech and /business pages.
"""
import json
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def _fetch_stream(url: str) -> list[dict]:
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    nd = soup.find("script", id="__NEXT_DATA__")
    if not nd:
        return []
    data = json.loads(nd.string)
    return data["props"]["pageProps"]["data"].get("stream", [])


def fetch_nikkei_tech(count: int = 20) -> list[dict]:
    """Return up to `count` Nikkei Asia tech articles with title, url, and published date."""
    seen = set()
    articles = []

    for url in [
        "https://asia.nikkei.com/business/tech",
        "https://asia.nikkei.com/business/technology/artificial-intelligence",
        "https://asia.nikkei.com/business/tech/semiconductors",
    ]:
        for item in _fetch_stream(url):
            article_url = item.get("url", "")
            if not article_url or article_url in seen:
                continue
            seen.add(article_url)

            ts = item.get("displayDate") or item.get("createdDate")
            published = (
                datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
                if ts else ""
            )

            articles.append({
                "title": item.get("headline", "").strip(),
                "url": article_url,
                "published": published,
            })

            if len(articles) >= count:
                return articles

    return articles


if __name__ == "__main__":
    articles = fetch_nikkei_tech(count=20)
    print(f"Found {len(articles)} Nikkei Asia tech articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print(f"     {a['published']}")
        print()
