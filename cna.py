"""
中央社財經新聞爬蟲。

使用中央社官方 FeedBurner RSS 取得財經新聞。
"""
import feedparser


def fetch_cna(count: int = 50) -> list[dict]:
    """Return up to `count` 中央社財經 articles."""
    feed = feedparser.parse("https://feeds.feedburner.com/rsscna/finance")
    articles = []
    for entry in feed.entries[:count]:
        articles.append({
            "title":     entry.get("title", "").strip(),
            "url":       entry.get("link", ""),
            "published": entry.get("published", ""),
        })
    return articles


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    articles = fetch_cna(count=20)
    print(f"Found {len(articles)} 中央社財經 articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print(f"     {a['published']}")
        print()
