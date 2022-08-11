from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTabWidget, QLineEdit
from loguru import logger

# 表头
from utils.path_util import resource_path


class SearchWindow(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # 记录上一次搜索的关键字 用于多个搜索结果跳转
        self.last_search_keyword = ''
        # 记录上一次搜索的结果位置
        self.last_search_index = 0
        # 检查数据是否有更新, 如果有更新, 需要重新搜索
        self.last_data_update_timestamp = None
        self.search_result = []

        self.current_tab = 0
        self.last_tab = 0

        self.setWindowIcon(QtGui.QIcon(resource_path('QBRssManager.ico')))

        self.tabs = QTabWidget()
        # self.tabs.resize(300, 200)

        # 搜索tab
        self.lineEdit = QLineEdit()
        self.lineEdit.setPlaceholderText('输入搜索关键字...')
        do_search_button = QPushButton("搜索")
        do_search_button.clicked.connect(self.parent.do_search)
        tab = QWidget()
        tab.layout = QVBoxLayout(self)
        tab.layout.addWidget(self.lineEdit)
        tab.layout.addWidget(do_search_button)
        tab.setLayout(tab.layout)
        self.tabs.addTab(tab, "搜索")

        # 替换tab
        self.lineEditReplaceSource = QLineEdit()
        self.lineEditReplaceSource.setPlaceholderText('输入搜索关键字...')
        self.lineEditReplaceTarget = QLineEdit()
        self.lineEditReplaceTarget.setPlaceholderText('替换为...')
        do_search_button2 = QPushButton("搜索")
        do_search_button2.clicked.connect(self.parent.do_search)
        do_replace_button = QPushButton("替换")
        do_replace_button.clicked.connect(self.parent.do_replace)
        do_replace_all_button = QPushButton("全部替换")
        do_replace_all_button.clicked.connect(self.parent.do_replace_all)
        tab = QWidget()
        tab.layout = QVBoxLayout(self)
        tab.layout.addWidget(self.lineEditReplaceSource)
        tab.layout.addWidget(self.lineEditReplaceTarget)
        tab.layout.addWidget(do_search_button2)
        tab.layout.addWidget(do_replace_button)
        tab.layout.addWidget(do_replace_all_button)
        tab.setLayout(tab.layout)
        self.tabs.addTab(tab, "替换")

        # 绑定tab切换事件
        self.tabs.currentChanged.connect(self.parent.search_tab_change)

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        # 这个是搜索输入框 切换tab时跟据index把之前的数据带过来覆盖
        self.text_edit_list = [self.lineEdit, self.lineEditReplaceSource]

        self.setWindowTitle("搜索和替换")

        flags = Qt.WindowFlags()
        # 窗口永远在最前面
        flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        # 按键绑定
        self.keyPressEvent = self.handle_key_press

        self.resize(250, 100)

    def closeEvent(self, event):
        # 搜索窗口的关闭按钮事件
        logger.info('关闭搜索窗口')
        self.parent.text_browser.clear()

    def handle_key_press(self, event):
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            logger.info('搜索')
            self.parent.do_search()
        elif event.key() in (Qt.Key_Escape,):
            self.close()
        elif event.key() == Qt.Key_F and (event.modifiers() & Qt.ControlModifier):
            self.tabs.setCurrentIndex(0)
        elif event.key() == Qt.Key_H and (event.modifiers() & Qt.ControlModifier):
            self.tabs.setCurrentIndex(1)
