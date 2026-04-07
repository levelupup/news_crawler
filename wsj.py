"""
WSJ Technology News scraper.

Fetches articles via WSJ's native RSS feed.
"""
import feedparser


def fetch_wsj_technology(count: int = 20) -> list[dict]:
    """Return up to `count` WSJ articles with title, url, and published date."""
    rss_url = "https://feeds.content.dowjones.io/public/rss/RSSWSJD"
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries[:count]:
        title = entry.get("title", "").strip()
        url = entry.get("link", "")
        published = entry.get("published", "")
        articles.append({"title": title, "url": url, "published": published})
    return articles


if __name__ == "__main__":
    articles = fetch_wsj_technology(count=20)
    print(f"Found {len(articles)} WSJ articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print(f"     {a['published']}")
        print()
