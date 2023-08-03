import subprocess

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QTextBrowser
from loguru import logger

import g

from utils.qb_util import check_qb_port_open
from utils.string_util import wildcard_match_check


def handle_links(url):
    if not url.scheme():
        url = QUrl.fromLocalFile(url.toString())
    url_str = url.toString()
    logger.info(f'点击了url {url_str}')

    if url_str.endswith('.torrent'):
        # torrent 文件需要特殊处理
        logger.info(f'处理torrent链接')
        if g.config['use_qb_api'] == 1:
            from QBRssManager import qb_client
            if check_qb_port_open(g.config['qb_api_ip'], g.config['qb_api_port']):
                # 使用qb的api读取feed
                try:
                    qb_client.auth_log_in(username=g.config['qb_api_username'], password=g.config['qb_api_password'])
                    logger.info(f'已连接api {qb_client.is_logged_in}')
                    res = qb_client.torrents_add(urls=(url_str,))
                    logger.info(res)
                except Exception as e:
                    logger.error(f'{e}')
        else:
            logger.info('cmd调用')
            try:
                subprocess.Popen([g.config['qb_executable'], url_str])
            except Exception as e:
                logger.error(f'{e}')
    else:
        # magnet链接和页面链接不用处理
        QDesktopServices.openUrl(url)


class CustomQTextBrowser(QTextBrowser):

    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.parent_app = parent_app

        # 设置使用外部程序打开链接
        self.setOpenLinks(False)
        self.anchorClicked.connect(handle_links)

    def filter_type_hint(self):
        # 过滤输入提示
        include_text = g.data_list[self.parent_app.tableWidget.currentItem().row()][2]
        exclude_text = g.data_list[self.parent_app.tableWidget.currentItem().row()][3]
        type_hints = self.parent_app.tableWidget.type_hints
        article_details = self.parent_app.tableWidget.article_details
        # 清空
        self.parent_app.text_browser.clear()
        if include_text.strip() == '' and exclude_text.strip() == '':
            # 特殊处理 为空则匹配所有
            # self.parent_app.text_browser.append('<br/>'.join(type_hints))
            for x in article_details:
                self.parent_app.text_browser.append(
                    f"""<a style="color:#00a3a3">{x['source_name']}</a> {x['title']} <a href="{x['url']}" alt="{x['url']}">链接</a> <a href="{x['torrent_url']}" alt="{x['torrent_url']}">下载</a>""")
        else:
            # 保留匹配的
            filtered_hints = []
            for i, type_hint in enumerate(type_hints):
                # 包含关键字
                flag1 = False
                # 不包含关键字
                flag2 = False
                if include_text:
                    # flag1 = all(x.lower() in type_hint.lower() for x in include_text.split(' '))
                    flag1 = wildcard_match_check(type_hint, include_text)
                if exclude_text:
                    # flag2 = all(x.lower() in type_hint.lower() for x in exclude_text.split(' '))
                    flag2 = wildcard_match_check(type_hint, exclude_text)
                if flag1 and not flag2:
                    # filtered_hints.append(type_hint)
                    filtered_hints.append(i)
            if filtered_hints:
                for i in filtered_hints:
                    x = article_details[i]
                    self.parent_app.text_browser.append(
                        f"""<a style="color:#00a3a3">{x['source_name']}</a> {x['title']} <a href="{x['url']}" alt="{x['url']}">链接</a> <a href="{x['torrent_url']}" alt="{x['torrent_url']}">下载</a>""")

            else:
                self.parent_app.text_browser.append('<p>暂时没有找到相关的feed</p>')

