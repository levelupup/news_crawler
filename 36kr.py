"""
36氪 (36kr.com) technology news scraper.

36kr.com now requires CAPTCHA for direct access.
Uses Google News RSS + googlenewsdecoder to get actual article URLs.
"""
import feedparser
from googlenewsdecoder import gnewsdecoder


def fetch_36kr(count: int = 20) -> list[dict]:
    """Return up to `count` articles from 36氪."""
    rss_url = (
        "https://news.google.com/rss/search"
        "?q=site:36kr.com+%E7%A7%91%E6%8A%80&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    )
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries[:count]:
        title = entry.get("title", "").removesuffix(" - 36kr.com").removesuffix(" - 36氪").strip()
        if not title or len(title) < 4:
            continue

        google_url = entry.get("link", "")
        published = entry.get("published", "")

        try:
            result = gnewsdecoder(google_url)
            url = result["decoded_url"] if result.get("status") else google_url
        except Exception:
            url = google_url

        # Normalize to www subdomain
        url = url.replace("m.36kr.com", "www.36kr.com").replace("eu.36kr.com", "www.36kr.com")

        articles.append({"title": title, "url": url, "published": published})

    return articles


if __name__ == "__main__":
    articles = fetch_36kr(count=20)
    print(f"Found {len(articles)} 36氪 articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print(f"     {a['published']}")
        print()
