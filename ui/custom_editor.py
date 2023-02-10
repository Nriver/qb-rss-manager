from PyQt5 import QtCore
from PyQt5 import QtWidgets
from loguru import logger

import g


class CustomEditor(QtWidgets.QPlainTextEdit):
    # 自定义一个 Editor
    # 输入过程中的事件捕获在这里定义
    # QLineEdit只能单行输入 QPlainTextEdit可以多行, 而且显示效果好看一点

    def __init__(self, parent, index, parent_app):
        super(CustomEditor, self).__init__(parent)
        self.parent = parent
        self.index = index
        self.parent_app = parent_app
        # 默认最小高度和宽度
        self.setMinimumWidth(150)
        self.setMinimumHeight(60)
        logger.info(f'输入框高度 {self.height()}')
        # 按键 事件
        self.keyPressEvent = self.custom_keypress
        # 输入法 不会触发keyPressEvent!
        # 需要对inputMethodEvent单独处理
        self.inputMethodEvent = self.custom_input_method_event

    def custom_input_method_event(self, event):
        # 自定义 输入法 事件处理
        # PyQt5.QtGui.QInputMethodEvent
        logger.info(f'customized IME {event}')
        # 原始事件
        super(CustomEditor, self).inputMethodEvent(event)
        # 原始事件处理完才能得到最新的文本
        # self.process_text(self.text())
        self.process_text(self.toPlainText())

    def custom_keypress(self, event):
        # 自定义 按键 事件处理
        logger.info('custom keypress')

        # 阻止换行
        if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            return

        # 原始事件
        super(CustomEditor, self).keyPressEvent(event)
        # 原始事件处理完才能得到最新的文本
        # self.process_text(self.text())
        self.process_text(self.toPlainText())

    def process_text(self, text):
        # 统一处理输入事件的文字
        logger.info(f'process_text() {text}')
        logger.info(f'self.index {self.index.row(), self.index.column()}')
        g.data_list[self.index.row()][self.index.column()] = text
        if self.index.column() in [2, 3]:
            self.parent_app.text_browser.filter_type_hint()
