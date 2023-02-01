import platform

from PyQt5 import QtCore
from PyQt5.QtWidgets import QTabBar, QLineEdit

import g


class CustomTabBar(QTabBar):
    """可编辑的QTabBar"""

    def __init__(self, parent):
        QTabBar.__init__(self, parent)
        self.editor = QLineEdit(self)

        if platform.system() == 'Windows':
            # windows 特有的输入法bug, 必须要用Dialog才能切换输入法, 再设置成无边框模式就能看上去和Popup一样了
            self.editor.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint)
        else:
            self.editor.setWindowFlags(QtCore.Qt.Popup)

        # 加上这个的话，只有回车才会使输入生效
        # self.editor.setFocusProxy(self)
        self.editor.editingFinished.connect(self.handleEditingFinished)
        self.editor.installEventFilter(self)
        # self.editor.activateWindow()

    def eventFilter(self, widget, event):
        if ((event.type() == QtCore.QEvent.MouseButtonPress and not self.editor.geometry().contains(
                event.globalPos())) or (
                event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Escape)):
            self.editor.hide()
            return True
        return QTabBar.eventFilter(self, widget, event)

    def mouseDoubleClickEvent(self, event):
        index = self.tabAt(event.pos())
        if index >= 0:
            self.editTab(index)

    def editTab(self, index):
        rect = self.tabRect(index)
        self.editor.setFixedSize(rect.size())
        self.editor.move(self.parent().mapToGlobal(rect.topLeft()))
        self.editor.setText(self.tabText(index))
        if not self.editor.isVisible():
            self.editor.show()

    def handleEditingFinished(self):
        index = self.currentIndex()
        if index >= 0:
            self.editor.hide()
            self.setTabText(index, self.editor.text())
            g.data_groups[index]['name'] = self.editor.text()
