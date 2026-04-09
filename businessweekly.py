"""
商業周刊新聞爬蟲。

使用商周 CMS API 的原生 RSS feed 取得財經與商業新聞。
每個分類 URL 均回傳 RSS 2.0 XML，透過 feedparser 解析。
"""
import feedparser

_FEEDS = [
    # 財經類
    (
        "https://cmsapi.businessweekly.com.tw/"
        "?CategoryId=24612ec9-2ac5-4e1f-ab04-310879f89b33"
        "&TemplateId=8E19CF43-50E5-4093-B72D-70A912962D55"
    ),
    # 商業類
    (
        "https://cmsapi.businessweekly.com.tw/"
        "?CategoryId=efd99109-9e15-422e-97f0-078b21322450"
        "&TemplateId=8E19CF43-50E5-4093-B72D-70A912962D55"
    ),
]


def fetch_businessweekly(count: int = 50) -> list[dict]:
    """Return up to `count` 商業周刊 articles (deduplicated across both feeds)."""
    seen: set[str] = set()
    articles = []
    for rss_url in _FEEDS:
        feed = feedparser.parse(rss_url)
        for entry in feed.entries:
            url = entry.get("link", "")
            if not url or url in seen:
                continue
            seen.add(url)
            articles.append({
                "title":     entry.get("title", "").strip(),
                "url":       url,
                "published": entry.get("published", ""),
            })
            if len(articles) >= count:
                return articles
    return articles


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    articles = fetch_businessweekly(count=20)
    print(f"Found {len(articles)} 商業周刊 articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print(f"     {a['published']}")
        print()
