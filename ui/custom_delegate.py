from PyQt5 import QtWidgets
from loguru import logger

from ui.custom_editor import CustomEditor


class CustomDelegate(QtWidgets.QStyledItemDelegate):
    # 要对表格编辑进行特殊处理, 必须自己实现一个QStyledItemDelegate/QItemDelegate

    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.parent_app = parent_app

    def createEditor(self, parent, option, index):
        # 编辑器初始化
        logger.info('createEditor()')
        editor = CustomEditor(parent, index, self.parent_app)
        return editor
