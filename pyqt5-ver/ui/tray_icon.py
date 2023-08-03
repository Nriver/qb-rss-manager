import sys

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.uic.properties import QtCore
from loguru import logger

from utils.path_util import resource_path


class TrayIcon(QSystemTrayIcon):

    def __init__(self, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.showMenu()
        self.activated.connect(self.iconClicked)
        self.setIcon(QtGui.QIcon(resource_path('QBRssManager.ico')))

    def showMenu(self):
        self.menu = QMenu()

        self.showWindowAction = QAction("显示程序窗口", self, triggered=self.show_main_window)
        self.quitAction = QAction("退出", self, triggered=self.quit)

        self.menu.addAction(self.showWindowAction)
        self.menu.addAction(self.quitAction)

        self.setContextMenu(self.menu)

    def iconClicked(self, reason):
        # 1是表示单击右键
        # 2是双击
        # 3是单击左键
        # 4是用鼠标中键点击
        if reason in (2, 3, 4):
            pw = self.parent()
            if pw.isVisible():
                pw.hide()
            else:
                pw.show()
        logger.info(reason)

    def show_main_window(self):
        self.parent().setWindowState(QtCore.Qt.WindowActive)
        self.parent().show()

    def quit(self):
        # 退出程序
        self.setVisible(False)
        sys.exit()
