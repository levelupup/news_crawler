"""
Electrek (electrek.co) news scraper.

Fetches articles via the native RSS feed.
"""
import feedparser


FEED_URL = "https://electrek.co/feed/"


def fetch_electrek(count: int = 20) -> list[dict]:
    """Return up to `count` articles from Electrek."""
    feed = feedparser.parse(FEED_URL)
    articles = []
    for entry in feed.entries[:count]:
        articles.append({
            "title":     entry.get("title", "").strip(),
            "url":       entry.get("link", ""),
            "published": entry.get("published", ""),
        })
    return articles


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    articles = fetch_electrek(count=20)
    print(f"Found {len(articles)} Electrek articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print(f"     {a['published']}")
        print()
