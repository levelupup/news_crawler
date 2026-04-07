"""
South China Morning Post news scraper.

Fetches articles via SCMP's native RSS feeds for Tech and China Tech sections.
"""
import feedparser


FEEDS = [
    "https://www.scmp.com/rss/36/feed/",
    "https://www.scmp.com/rss/320663/feed/",
]


def fetch_scmp(count: int = 20) -> list[dict]:
    """Return up to `count` SCMP articles with title, url, and published date."""
    seen = set()
    articles = []
    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            url = entry.get("link", "")
            if not url or url in seen:
                continue
            seen.add(url)
            articles.append({
                "title":     entry.get("title", "").strip(),
                "url":       url,
                "published": entry.get("published", ""),
            })
            if len(articles) >= count:
                return articles
    return articles


if __name__ == "__main__":
    articles = fetch_scmp(count=20)
    print(f"Found {len(articles)} SCMP articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print(f"     {a['published']}")
        print()
