"""
ZDNet Korea news scraper.

Fetches articles via ZDNet Korea's FeedBurner RSS feed.
"""
import feedparser


def fetch_zdkorea(count: int = 20) -> list[dict]:
    """Return up to `count` ZDNet Korea articles with title, url, and published date."""
    feed = feedparser.parse("https://feeds.feedburner.com/zdkorea")
    articles = []
    for entry in feed.entries[:count]:
        articles.append({
            "title":     entry.get("title", "").strip(),
            "url":       entry.get("link", ""),
            "published": entry.get("published", ""),
        })
    return articles


if __name__ == "__main__":
    articles = fetch_zdkorea(count=20)
    print(f"Found {len(articles)} ZDNet Korea articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print(f"     {a['published']}")
        print()
