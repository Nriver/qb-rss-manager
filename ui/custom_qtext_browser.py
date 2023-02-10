from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QTextBrowser

import g
from utils.string_util import wildcard_match_check


def handle_links(url):
    if not url.scheme():
        url = QUrl.fromLocalFile(url.toString())
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
                    f"""<a style="color:#00a3a3">{x['source_name']}</a> {x['title']} <a href="{x['url']} alt="{x['url']}"">链接</a>""")
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
                        f"""<a style="color:#00a3a3">{x['source_name']}</a> {x['title']} <a href="{x['url']}" alt="{x['url']}">链接</a>""")

            else:
                self.parent_app.text_browser.append('<p>暂时没有找到相关的feed</p>')
