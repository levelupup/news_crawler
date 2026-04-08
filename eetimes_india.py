"""
EE Times India (eetindia.co.in) news scraper.
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


def fetch_eetimes_india(count: int = 20) -> list[dict]:
    """Return up to `count` articles from EE Times India."""
    response = requests.get('https://www.eetindia.co.in/news/', timeout=15)
    soup = BeautifulSoup(response.text, 'lxml')
    articles = soup.find_all('h2')
    result = []
    for article in articles[:count]:
        a = article.find('a')
        if not a:
            continue
        result.append({
            'title': fix_title(article.text.strip()),
            'url': a.get('href', ''),
            'published': '',
        })
    return result


if __name__ == '__main__':
    articles = fetch_eetimes_india(count=20)
    print(f"Found {len(articles)} EE Times India articles:\n")
    for i, a in enumerate(articles, 1):
        print(f"{i:3}. {a['title']}")
        print(f"     {a['url']}")
        print()
