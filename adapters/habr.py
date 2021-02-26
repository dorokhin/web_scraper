from useragent import random_user_agent
from lxml import etree, html
import feedparser


def read_rss(url: str, headers=None) -> list:
    items = list()
    headers = headers if headers else {
        'User-Agent': random_user_agent(),
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Accept': 'text/html,application/rss+xml,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    feed = feedparser.parse(url, request_headers=headers)
    if feed:
        for item in feed['items']:
            link = item['guid']
            title = item['title']
            items.append({'url': link, 'title': title})
    else:
        print('Nothing found in feed', url)
        return
    return items


def extract_post_data(content: str) -> dict:
    tree = html.fragment_fromstring(content)
    post_text = tree.xpath("//div[@id='post-content-body']")
    post_text = etree.tostring(post_text[0], pretty_print=True, encoding='utf-8').decode('utf-8')
    post_author = tree.xpath("//header/*/span[contains(@class, 'user-info__nickname') "
                             "and contains(@class, 'user-info__nickname_small')]/text()")[0]
    post_author_url = tree.xpath("//a[contains(@class, 'post__user-info') and contains(@class, 'user-info')]/@href")[0]
    post_tags = tree.xpath("//ul[contains(@class, 'js-post-tags')]/*/a[contains(@class, 'inline-list__item-link') "
                           "and contains(@class, 'post__tag')]/text()")
    post_posted_at = tree.xpath("//span[contains(@class, 'post__time')]/@data-time_published")[0]
    return {
        'post_text': post_text,
        'post_author': post_author,
        'post_author_url': post_author_url,
        'post_tags': post_tags,
        'post_posted_at': post_posted_at,
    }


if __name__ == '__main__':
    pass
