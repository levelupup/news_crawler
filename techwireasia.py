"""
Tech Wire Asia (techwireasia.com) news scraper.
"""
import html as html_module
import requests
from bs4 import BeautifulSoup


def fix_title(t):
    if t is None:
        return t
    try:
        t = t.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    return html_module.unescape(t)


def fetch_techwireasia(count: int = 20) -> list[dict]:
    """Return up to `count` articles from Tech Wire Asia."""
    response = requests.get('https://techwireasia.com/latest-tech/', timeout=15)
    soup = BeautifulSoup(response.text, 'lxml')
    articles = soup.find_all('a', {'rel': 'bookmark'})
    result = []
    for h in articles[:count]:
        result.append({
            'title': fix_title(h.get('title', '')),
            'url': h.get('href', ''),
            'published': '',
        })
    return result


if __name__ == '__main__':
    articles = fetch_techwireasia(count=20)
    print(f"Found {len(articles)} Tech Wire Asia articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print()
