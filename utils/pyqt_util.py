import sys

from PyQt5 import QtWidgets


def catch_exceptions(t, val, tb):
    """获取pyqt5的exception"""
    old_hook = sys.excepthook
    QtWidgets.QMessageBox.critical(None,
                                   "An exception was raised",
                                   "Exception type: {}".format(t))
    old_hook(t, val, tb)
