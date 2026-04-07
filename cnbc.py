"""
CNBC Technology news scraper.

Fetches articles via CNBC's native RSS feed.
"""
import feedparser


def fetch_cnbc(count: int = 20) -> list[dict]:
    """Return up to `count` CNBC technology articles with title, url, and published date."""
    feed = feedparser.parse(
        "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=19854910"
    )
    articles = []
    for entry in feed.entries[:count]:
        articles.append({
            "title":     entry.get("title", "").strip(),
            "url":       entry.get("link", ""),
            "published": entry.get("published", ""),
        })
    return articles


if __name__ == "__main__":
    articles = fetch_cnbc(count=20)
    print(f"Found {len(articles)} CNBC technology articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print(f"     {a['published']}")
        print()
