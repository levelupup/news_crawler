"""
Nikkei Asia news scraper.

Fetches articles via Nikkei Asia's native RSS feed.
"""
import feedparser


def fetch_nikkei_tech(count: int = 20) -> list[dict]:
    """Return up to `count` Nikkei Asia articles with title, url, and published date."""
    feed = feedparser.parse("https://asia.nikkei.com/rss/feed/nar")
    articles = []
    for entry in feed.entries[:count]:
        articles.append({
            "title":     entry.get("title", "").strip(),
            "url":       entry.get("link", ""),
            "published": entry.get("published", ""),
        })
    return articles


if __name__ == "__main__":
    articles = fetch_nikkei_tech(count=20)
    print(f"Found {len(articles)} Nikkei Asia articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print(f"     {a['published']}")
        print()
