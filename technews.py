"""
TechNews 科技新報爬蟲。

使用 TechNews 官方 RSS 取得科技新聞。
"""
import feedparser


def fetch_technews(count: int = 50) -> list[dict]:
    """Return up to `count` TechNews 科技新報 articles."""
    feed = feedparser.parse("https://technews.tw/news-rss/")
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
    articles = fetch_technews(count=20)
    print(f"Found {len(articles)} TechNews 科技新報 articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print(f"     {a['published']}")
        print()
