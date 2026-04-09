"""
經濟日報新聞爬蟲。

經濟日報（money.udn.com）列表頁需 JavaScript 渲染，
改用 Google News RSS + googlenewsdecoder 取得實際文章 URL。
"""
import feedparser
from googlenewsdecoder import gnewsdecoder

_RSS_URL = (
    "https://news.google.com/rss/search"
    "?q=site:money.udn.com&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
)

_SUFFIXES = [" - 經濟日報", " - udn 經濟日報", " - 聯合新聞網"]


def fetch_udn_money(count: int = 50) -> list[dict]:
    """Return up to `count` 經濟日報 articles."""
    feed = feedparser.parse(_RSS_URL)
    seen: set[str] = set()
    articles = []
    for entry in feed.entries:
        google_url = entry.get("link", "")
        if not google_url or google_url in seen:
            continue
        seen.add(google_url)

        title = entry.get("title", "").strip()
        for suffix in _SUFFIXES:
            if title.endswith(suffix):
                title = title[: -len(suffix)].strip()
                break

        try:
            result = gnewsdecoder(google_url)
            url = result["decoded_url"] if result.get("status") else google_url
        except Exception:
            url = google_url

        articles.append({
            "title":     title,
            "url":       url,
            "published": entry.get("published", ""),
        })
        if len(articles) >= count:
            break
    return articles


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    articles = fetch_udn_money(count=20)
    print(f"Found {len(articles)} 經濟日報 articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print(f"     {a['published']}")
        print()
