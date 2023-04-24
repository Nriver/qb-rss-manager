import re
import socket

from loguru import logger


def check_qb_port_open(qb_api_ip, qb_api_port):
    # 检查端口可用性
    a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 若填写域名则去掉协议名
    qb_api_ip = qb_api_ip.replace("https://", "")
    location = (qb_api_ip, int(qb_api_port))
    result_of_check = a_socket.connect_ex(location)
    if result_of_check == 0:
        logger.info('qb端口可用')
        return True
    else:
        logger.info('qb端口不可用')
        return False


def parse_feed_url(s):
    # 多个feed数据解析
    # 多行文本也可以解析
    feeds = re.split(', |\||\s', s)
    res = []
    for x in feeds:
        # 去除空格
        x = x.strip()
        # 顺便去重
        if x and x not in res:
            res.append(x)
    return res


def parse_articles_for_type_hint(articles, source_name):
    article_titles = []
    article_details = []
    for article in articles:
        url = ''
        # feed的链接, 有的在id里面, 有的在url里面, 有的在link里面
        for y in ['id', 'link', 'url']:
            if y in article and str(article[y]).startswith('http'):
                url = article[y]
                break

        article_titles.append(article['title'])
        article_details.append({
            'title': article['title'],
            'url': url,
            'source_name': source_name,
            'torrent_url': article['torrentURL'],
        })
    return article_titles, article_details

def parse_feeds_url(feeds):
    """
    提取feed的订阅链接
    feed可能包含文件夹, 这里要处理嵌套的多层feed格式
    """
    results = []
    for x in feeds:
        feed = feeds[x]
        if 'url' in feed and 'url' in feed:
            # 普通feed
            results.append(feed['url'])
        else:
            # 文件夹
            tmp = parse_feeds_url(feed)
            results.extend(tmp)
    return results

if __name__ == '__main__':
    print(parse_feed_url('h, s|v a'))
    print(parse_feed_url('http'))
