"""
The Information scraper.

The Information's native RSS feed (theinformation.com/feed) is blocked by Cloudflare (403).
Falls back to Google News RSS + googlenewsdecoder to retrieve actual article URLs.
"""
import feedparser
from googlenewsdecoder import gnewsdecoder


def fetch_theinformation(count: int = 20) -> list[dict]:
    """Return up to `count` The Information articles with title, url, and published date."""
    rss_url = (
        "https://news.google.com/rss/search"
        "?q=site:theinformation.com&hl=en-US&gl=US&ceid=US:en"
    )
    feed = feedparser.parse(rss_url)
    articles = []
    for entry in feed.entries[:count]:
        title = entry.get("title", "").removesuffix(" - The Information").strip()
        google_url = entry.get("link", "")

        try:
            result = gnewsdecoder(google_url)
            url = result["decoded_url"] if result.get("status") else google_url
        except Exception:
            url = google_url

        articles.append({"title": title, "url": url})

    return articles


if __name__ == "__main__":
    articles = fetch_theinformation(count=20)
    print(f"Found {len(articles)} The Information articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print()
