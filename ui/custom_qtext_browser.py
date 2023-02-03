from PyQt5.QtWidgets import QTextBrowser

import g
from utils.string_util import wildcard_match_check


class CustomQTextBrowser(QTextBrowser):

    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.parent_app = parent_app

    def filter_type_hint(self):
        # 过滤输入提示
        include_text = g.data_list[self.parent_app.tableWidget.currentItem().row()][2]
        exclude_text = g.data_list[self.parent_app.tableWidget.currentItem().row()][3]
        type_hints = self.parent_app.tableWidget.type_hints
        # 清空
        self.parent_app.text_browser.clear()
        if include_text.strip() == '' and exclude_text.strip() == '':
            # 特殊处理 为空则匹配所有
            self.parent_app.text_browser.append('\n'.join(type_hints))
        else:
            # 保留匹配的
            filtered_hints = []
            for type_hint in type_hints:
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
                    filtered_hints.append(type_hint)
            if filtered_hints:
                self.parent_app.text_browser.append('\n'.join(filtered_hints))
            else:
                self.parent_app.text_browser.append('暂时没有找到相关的feed')
