from PyQt5 import QtWidgets
from loguru import logger

from ui.custom_editor import CustomEditor
from ui.custom_editor_high import CustomEditorHigh


class CustomDelegate(QtWidgets.QStyledItemDelegate):
    # 要对表格编辑进行特殊处理, 必须自己实现一个QStyledItemDelegate/QItemDelegate

    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.parent_app = parent_app

    def createEditor(self, parent, option, index):
        # 编辑器初始化
        logger.info(f'createEditor() {index.row()} {index.column()}')
        if index.column() in [2, 3]:
            editor = CustomEditor(parent, index, self.parent_app)
            return editor
        elif index.column() in [5, 6]:
            editor = CustomEditorHigh(parent, index, self.parent_app)
            return editor
