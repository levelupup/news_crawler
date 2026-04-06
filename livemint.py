"""
Livemint news scraper.

Fetches articles via Livemint's RSS feeds for Companies, Technology, and AI sections.
"""
import feedparser


FEEDS = {
    "companies":  "https://www.livemint.com/rss/companies",
    "technology": "https://www.livemint.com/rss/technology",
    "ai":         "https://www.livemint.com/rss/AI",
}


def _fetch_feed(url: str, count: int) -> list[dict]:
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:count]:
        articles.append({
            "title":     entry.get("title", "").strip(),
            "url":       entry.get("link", ""),
            "published": entry.get("published", ""),
        })
    return articles


def fetch_livemint_companies(count: int = 20) -> list[dict]:
    """Return up to `count` Livemint Companies articles."""
    return _fetch_feed(FEEDS["companies"], count)


def fetch_livemint_technology(count: int = 20) -> list[dict]:
    """Return up to `count` Livemint Technology articles."""
    return _fetch_feed(FEEDS["technology"], count)


def fetch_livemint_ai(count: int = 20) -> list[dict]:
    """Return up to `count` Livemint AI articles."""
    return _fetch_feed(FEEDS["ai"], count)


def fetch_livemint(count: int = 20) -> list[dict]:
    """Return up to `count` Livemint articles across all sections (deduplicated)."""
    seen = set()
    articles = []
    for key in FEEDS:
        for a in _fetch_feed(FEEDS[key], count):
            if a["url"] not in seen:
                seen.add(a["url"])
                articles.append(a)
            if len(articles) >= count:
                return articles
    return articles


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    for name, fn in [
        ("Companies", fetch_livemint_companies),
        ("Technology", fetch_livemint_technology),
        ("AI", fetch_livemint_ai),
    ]:
        articles = fn(count=5)
        print(f"=== Livemint {name} ({len(articles)} articles) ===")
        for i, a in enumerate(articles, 1):
            print(f"{i:3}. {a['title']}")
            print(f"     {a['url']}")
            print(f"     {a['published']}")
        print()
