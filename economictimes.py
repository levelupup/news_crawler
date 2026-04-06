"""
Economic Times news scraper.

Fetches articles via Economic Times RSS feeds for Prime, Tech, AI, and Industry sections.
"""
import feedparser


FEEDS = {
    "prime":    "https://economictimes.indiatimes.com/prime/rssfeeds/69891145.cms",
    "tech":     "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",
    "ai":       "https://economictimes.indiatimes.com/ai/rssfeeds/119215726.cms",
    "industry": "https://economictimes.indiatimes.com/industry/rssfeeds/13352306.cms",
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


def fetch_economictimes_prime(count: int = 20) -> list[dict]:
    """Return up to `count` Economic Times Prime articles."""
    return _fetch_feed(FEEDS["prime"], count)


def fetch_economictimes_tech(count: int = 20) -> list[dict]:
    """Return up to `count` Economic Times Tech articles."""
    return _fetch_feed(FEEDS["tech"], count)


def fetch_economictimes_ai(count: int = 20) -> list[dict]:
    """Return up to `count` Economic Times AI articles."""
    return _fetch_feed(FEEDS["ai"], count)


def fetch_economictimes_industry(count: int = 20) -> list[dict]:
    """Return up to `count` Economic Times Industry articles."""
    return _fetch_feed(FEEDS["industry"], count)


def fetch_economictimes(count: int = 20) -> list[dict]:
    """Return up to `count` Economic Times articles across all sections (deduplicated)."""
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
        ("Prime",    fetch_economictimes_prime),
        ("Tech",     fetch_economictimes_tech),
        ("AI",       fetch_economictimes_ai),
        ("Industry", fetch_economictimes_industry),
    ]:
        articles = fn(count=5)
        print(f"=== Economic Times {name} ({len(articles)} articles) ===")
        for i, a in enumerate(articles, 1):
            print(f"{i:3}. {a['title']}")
            print(f"     {a['url']}")
            print(f"     {a['published']}")
        print()
