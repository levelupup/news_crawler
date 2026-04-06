"""
Bloomberg Technology news scraper.

Bloomberg blocks all direct/Playwright access with bot detection.
Uses Google News RSS + googlenewsdecoder to get actual Bloomberg article URLs.
"""
import feedparser
from googlenewsdecoder import gnewsdecoder


def fetch_bloomberg(count: int = 150) -> list[dict]:
    """Return up to `count` Bloomberg technology articles with title, url, and published date."""
    rss_url = (
        "https://news.google.com/rss/search"
        "?q=site:bloomberg.com+technology&hl=en-US&gl=US&ceid=US:en"
    )
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries[:count]:
        title = entry.get("title", "").removesuffix(" - Bloomberg.com").removesuffix(" - Bloomberg").strip()
        google_url = entry.get("link", "")
        published = entry.get("published", "")

        try:
            result = gnewsdecoder(google_url)
            url = result["decoded_url"] if result.get("status") else google_url
        except Exception:
            url = google_url

        articles.append({"title": title, "url": url, "published": published})

    return articles


if __name__ == "__main__":
    articles = fetch_bloomberg(count=150)
    print(f"Found {len(articles)} Bloomberg technology articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print(f"     {a['published']}")
        print()
