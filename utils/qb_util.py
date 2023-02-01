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
    return re.split(', |\||\s', s)


if __name__ == '__main__':
    print(parse_feed_url('h, s|v a'))
    print(parse_feed_url('http'))
