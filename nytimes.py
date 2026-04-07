"""
NYTimes Chinese (cn.nytimes.com) news scraper.

Fetches articles via the NYT Chinese RSS feed (Traditional Chinese).
"""
import feedparser


RSS_URL = "https://cn.nytimes.com/rss/zh-hant/"


def fetch_nytimes(count: int = 50) -> list[dict]:
    """Return up to `count` NYT Chinese articles."""
    feed = feedparser.parse(RSS_URL)
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
    articles = fetch_nytimes(count=20)
    print(f"Found {len(articles)} NYTimes Chinese articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print(f"     {a['published']}")
        print()
