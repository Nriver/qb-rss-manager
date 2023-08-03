import traceback

from PyQt5 import QtWidgets
from loguru import logger


def catch_exceptions(exc_type, exc_value, exc_tb):
    """获取pyqt5的exception"""

    # 输出Traceback信息
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logger.error(f"error catched!:")
    logger.error(f"error message:\n{tb}")

    # 界面提示报错
    QtWidgets.QMessageBox.critical(None,
                                   "An exception was raised",
                                   "Exception type: {}".format(exc_type))
    # 这里的要去掉 不然可能无限出发弹窗
    # old_hook = sys.excepthook
    # old_hook(t, val, tb)
