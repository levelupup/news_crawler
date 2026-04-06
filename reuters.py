"""
Reuters Technology News scraper.

Reuters blocks direct requests and Playwright with DataDome CAPTCHA.
This script fetches articles via Google News RSS and decodes the redirect URLs
to get the actual Reuters article URLs.
"""
import feedparser
from googlenewsdecoder import gnewsdecoder


def fetch_reuters_technology(count: int = 20) -> list[dict]:
    """Return up to `count` Reuters technology articles with title, url, and published date."""
    rss_url = (
        "https://news.google.com/rss/search"
        "?q=site:reuters.com+technology&hl=en-US&gl=US&ceid=US:en"
    )
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries[:count]:
        title = entry.get("title", "").removesuffix(" - Reuters").strip()
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
    articles = fetch_reuters_technology(count=20)
    print(f"Found {len(articles)} Reuters technology articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print(f"     {a['published']}")
        print()
