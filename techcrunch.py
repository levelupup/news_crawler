"""
TechCrunch news scraper.

Uses TechCrunch's official RSS feeds — no CAPTCHA bypass needed.
"""
import feedparser


FEEDS = [
    "https://techcrunch.com/feed/",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://techcrunch.com/category/startups/feed/",
]


def fetch_techcrunch(count: int = 20) -> list[dict]:
    """Return up to `count` TechCrunch articles with title, url, published date, and tags."""
    seen = set()
    articles = []

    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            url = entry.get("link", "")
            if not url or url in seen:
                continue
            seen.add(url)

            title = entry.get("title", "").strip()
            published = entry.get("published", "")
            tags = [t["term"] for t in entry.get("tags", []) if t.get("term")]

            articles.append({
                "title": title,
                "url": url,
                "published": published,
                "tags": tags,
            })

            if len(articles) >= count:
                return articles

    return articles


if __name__ == "__main__":
    articles = fetch_techcrunch(count=20)
    print(f"Found {len(articles)} TechCrunch articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print(f"     {a['published']}")
        if a["tags"]:
            print(f"     [{', '.join(a['tags'])}]")
        print()
