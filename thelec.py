"""
The Elec news scraper.

Fetches articles via The Elec's native RSS feed.
"""
import feedparser


def fetch_thelec(count: int = 20) -> list[dict]:
    """Return up to `count` The Elec articles with title, url, and published date."""
    feed = feedparser.parse("https://www.thelec.net/rss/allArticle.xml")
    articles = []
    for entry in feed.entries[:count]:
        articles.append({
            "title":     entry.get("title", "").strip(),
            "url":       entry.get("link", ""),
            "published": entry.get("published", ""),
        })
    return articles


if __name__ == "__main__":
    articles = fetch_thelec(count=20)
    print(f"Found {len(articles)} The Elec articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print(f"     {a['published']}")
        print()
