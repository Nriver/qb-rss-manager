from PyQt5 import QtCore
from PyQt5 import QtWidgets
from loguru import logger


class CustomEditorHigh(QtWidgets.QPlainTextEdit):
    # 一个高一点的编辑框

    def __init__(self, parent, index, parent_app):
        super(CustomEditorHigh, self).__init__(parent)
        self.parent = parent
        self.index = index
        self.parent_app = parent_app
        # 默认高度
        self.setMinimumWidth(150)
        self.setMinimumHeight(90)
        logger.info(f'输入框高度 {self.height()}')

        # 按键 事件
        self.keyPressEvent = self.custom_keypress

    def custom_keypress(self, event):
        # 自定义 按键 事件处理
        logger.info('custom keypress')

        # 阻止换行
        if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            return

        # 原始事件
        super(CustomEditorHigh, self).keyPressEvent(event)
