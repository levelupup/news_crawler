"""
The Edge Malaysia (theedgemalaysia.com) technology news scraper.

The listing page is Next.js SSR — article data is embedded in __NEXT_DATA__ JSON
rather than in the HTML DOM, so BeautifulSoup selectors don't work.
We parse the JSON directly to extract articles.
"""
import json
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

_URL = "https://theedgemalaysia.com/categories/technology"
_ROOT = "https://theedgemalaysia.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch_edge_markets(count: int = 20) -> list[dict]:
    """Return up to `count` technology articles from The Edge Malaysia."""
    r = requests.get(_URL, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    next_data_tag = soup.find("script", id="__NEXT_DATA__")
    if not next_data_tag:
        return []

    data = json.loads(next_data_tag.string)
    corp = data.get("props", {}).get("pageProps", {}).get("corporateData", [])

    articles = []
    for item in corp[:count]:
        alias = item.get("alias", "")
        if not alias:
            continue
        url = f"{_ROOT}/{alias}"
        title = item.get("title", "").strip()

        ts_ms = item.get("created", 0)
        if ts_ms:
            dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
            published = dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
        else:
            published = ""

        articles.append({"title": title, "url": url, "published": published})

    return articles


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    articles = fetch_edge_markets(count=20)
    print(f"Found {len(articles)} The Edge Malaysia articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print(f"     {a['published']}")
        print()
