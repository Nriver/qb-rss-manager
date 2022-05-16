import json
import os
import re
import socket
import subprocess
import sys
import time
from datetime import datetime
from zipfile import ZipFile

import qbittorrentapi
import win32gui
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSlot, Qt, QPoint, QByteArray
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QDesktopWidget, \
    QStyleFactory, QPushButton, QHBoxLayout, QMessageBox, QMenu, QAction, QSystemTrayIcon, QTextBrowser, QSplitter, \
    QTabWidget, QLineEdit
from loguru import logger
from win32con import WM_MOUSEMOVE

# 表头
headers = ['播出时间', '剧集名称', '包含关键字', '排除关键字', '集数修正', '保存路径', 'RSS订阅地址', '种子类型']

# 配置
config = {}


def clean_data_list():
    cleaned_data = []
    for x in data_list:
        if all(y == '' for y in x):
            continue
        cleaned_data.append(x)
    return cleaned_data


def save_config(update_data=True):
    logger.info(f'保存配置 更新数据 {update_data}')
    with open('config.json', 'w', encoding='utf-8') as f:
        if update_data:
            config['data_list'] = clean_data_list()
        f.write(json.dumps(config, ensure_ascii=False, indent=4))


try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.loads(f.read())
        # 拷贝一份数据, 防止不需要更新的时候把配置更新了
        data_list = config['data_list'][::]
        if 'auto_save' not in config:
            config['auto_save'] = 0
        if 'max_row_size' not in config:
            config['max_row_size'] = 100
        try:
            # 修正旧数据, 临时使用, 之后要删除
            if len(config['data_list'][0]) == 6:
                data_list_fix = []
                for x in config['data_list']:
                    row = x[:4] + ['', ] + x[4:]
                    data_list_fix.append(row)
                data_list = data_list_fix
                config['data_list'] = data_list[::]
            if len(config['data_list'][0]) == 7:
                data_list_fix = []
                for x in config['data_list']:
                    row = x[::] + ['', ]
                    data_list_fix.append(row)
                data_list = data_list_fix
                config['data_list'] = data_list[::]
                config['column_width_list'] = config['column_width_list'] + [80, ]
        except:
            pass

        if 'full_window_width' not in config:
            config['full_window_width'] = 1400
        if 'full_window_height' not in config:
            config['full_window_height'] = 800
        if 'column_width_list' not in config:
            column_width_list = [80, 260, 210, 65, 62, 370, 290, 80]
            config['column_width_list'] = column_width_list
        if 'center_columns' not in config:
            config['center_columns'] = [0, 3, 4]
        if 'close_to_tray' not in config:
            config['close_to_tray'] = 1
        if 'date_auto_zfill' not in config:
            config['date_auto_zfill'] = 0
        if 'feeds_json_path' not in config:
            config['feeds_json_path'] = os.path.expandvars(r'%appdata%\qBittorrent\rss\feeds.json')
        if 'rss_article_folder' not in config:
            config['rss_article_folder'] = os.path.expandvars(r'%LOCALAPPDATA%\qBittorrent\rss\articles')
        if 'use_qb_api' not in config:
            config['use_qb_api'] = 1
        if 'qb_api_ip' not in config:
            config['qb_api_ip'] = '127.0.0.1'
        if 'qb_api_port' not in config:
            config['qb_api_port'] = 38080
        if 'text_browser_height' in config:
            del config['text_browser_height']
except:

    # 默认配置
    # rules_path = r'E:\soft\bt\qBittorrent\profile\qBittorrent\config\rss\download_rules.json'
    rules_path = os.path.expandvars(r'%appdata%\qBittorrent\rss\download_rules.json')
    feeds_json_path = os.path.expandvars(r'%appdata%\qBittorrent\rss\feeds.json')
    rss_article_folder = os.path.expandvars(r'%LOCALAPPDATA%\qBittorrent\rss\articles')
    # 保存后打开qb主程序 1为自动打开 其它值不自动打开
    open_qb_after_export = 1
    # qb主程序路径
    # qb_executable = r'E:\soft\bt\qBittorrent\qbittorrent_x64.exe'
    qb_executable = os.path.expandvars(r'%ProgramW6432%\qBittorrent\qbittorrent.exe')
    data_list = [
    ]
    # 自动保存
    auto_save = 0
    max_row_size = 100
    config['rules_path'] = rules_path
    config['open_qb_after_export'] = open_qb_after_export
    config['qb_executable'] = qb_executable
    config['data_list'] = data_list
    config['auto_save'] = auto_save
    config['max_row_size'] = max_row_size
    config['date_auto_zfill'] = 0
    config['feeds_json_path'] = feeds_json_path
    config['rss_article_folder'] = rss_article_folder

    with open('config.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(config, ensure_ascii=False, indent=4))
    # 生成配置直接退出
    sys.exit()

# 补到 max_row_size 个数据
if len(data_list) < config['max_row_size']:
    for _ in range(config['max_row_size'] - len(data_list)):
        data_list.append(['' for x in range(len(headers))])

# 初始化qb_api客户端
if config['use_qb_api']:
    qb_client = qbittorrentapi.Client(
        host=config['qb_api_ip'],
        port=config['qb_api_port'],
    )


def format_path(s):
    return s.replace('\\', '/').replace('//', '/')


def try_convert_time(s):
    """
    简单粗暴的字符串转换年月
    比如 2021.11 2021-11 2021/11 转换成2021年11月
    """
    res = re.match(r'^(\d{4})[\.\-\_\\/](\d{1,2})$', s)
    if res:
        year = str(res[1])
        month = str(res[2])

        if config['date_auto_zfill'] == 1:
            month = month.zfill(2)
        s = f'{year}年{month}月'
    return s


qb_executable_name = format_path(config['qb_executable']).rsplit('/', 1)[-1]


class CustomEditor(QtWidgets.QLineEdit):
    # 自定义一个 Editor
    # 输入过程中的事件捕获在这里定义
    # QLineEdit

    def __init__(self, parent, index, parent_app):
        super(CustomEditor, self).__init__(parent)
        self.parent = parent
        self.index = index
        self.parent_app = parent_app
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
        self.process_text(self.text())

    def custom_keypress(self, event):
        # 自定义 按键 事件处理
        logger.info('custom keypress')
        # 原始事件
        super(CustomEditor, self).keyPressEvent(event)
        # 原始事件处理完才能得到最新的文本
        self.process_text(self.text())

    def process_text(self, text):
        # 统一处理输入事件的文字
        logger.info(f'process_text() {text}')
        logger.info(f'self.index {self.index.row(), self.index.column()}')
        data_list[self.index.row()][self.index.column()] = text
        if self.index.column() in [2, 3]:
            self.parent_app.text_browser.filter_type_hint()


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


class CustomQTextBrowser(QTextBrowser):

    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.parent_app = parent_app

    def filter_type_hint(self):
        include_text = data_list[self.parent_app.tableWidget.currentItem().row()][2]
        exclude_text = data_list[self.parent_app.tableWidget.currentItem().row()][3]
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
                    flag1 = all(x.lower() in type_hint.lower() for x in include_text.split(' '))
                if exclude_text:
                    flag2 = all(x.lower() in type_hint.lower() for x in exclude_text.split(' '))
                if flag1 and not flag2:
                    filtered_hints.append(type_hint)
            if filtered_hints:
                self.parent_app.text_browser.append('\n'.join(filtered_hints))
            else:
                self.parent_app.text_browser.append('暂时没有找到相关的feed')


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


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'qBittorrent 订阅下载规则管理 v1.1.4 by Nriver'
        # 图标
        self.setWindowIcon(QtGui.QIcon(resource_path('QBRssManager.ico')))
        self.left = 0
        self.top = 0
        self.width = config['full_window_width']
        self.height = config['full_window_height']
        logger.info(f'窗口大小 {self.width} {self.height}')
        # 防止初始化时触发header宽度变化事件导致参数被覆盖, 等初始化完毕再设置为False
        self.preventHeaderResizeEvent = True
        # ctrl+c
        self.copied_cells = []
        self.initUI()
        self.tray_icon = TrayIcon(self)
        self.tray_icon.show()
        # 记录数据更新时间
        self.data_update_timestamp = int(datetime.now().timestamp() * 1000)

        # 防止窗口超出屏幕
        pos = self.pos()
        if pos.x() < 0:
            pos.setX(0)
        if pos.y() < 0:
            pos.setY(0)
        logger.info(f'主窗口位置 {pos.x(), pos.y()}')
        self.move(pos)

        # 初始化搜索框
        self.search_window = SearchWindow(self)

    def center(self):
        # 窗口居中
        qr = self.normalGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createButton()
        self.createTable()
        self.layout_button = QHBoxLayout()
        self.layout_button.addWidget(self.move_up_button)
        self.layout_button.addWidget(self.move_down_button)
        self.layout_button.addWidget(self.clean_row_button)
        self.layout_button.addWidget(self.load_config_button)
        self.layout_button.addWidget(self.save_button)
        self.layout_button.addWidget(self.backup_button)
        self.layout_button.addWidget(self.output_button)

        # 文本框 固定位置方便输出
        self.text_browser = CustomQTextBrowser(self)
        self.text_browser.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        # self.text_browser.setMaximumHeight(config['text_browser_height'])

        # 文本框 去掉右键菜单
        self.text_browser.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.text_browser.customContextMenuRequested.connect(self.generateTextBrowserMenu)
        # 文本框滚动条去掉右键菜单
        self.text_browser.verticalScrollBar().setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.text_browser.horizontalScrollBar().setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.text_browser.resizeEvent = self.custom_text_browser_resize_event

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.layout_button)

        # 增加QSplitter, 让文本框组件直接通过拖拽修改大小
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.tableWidget)
        self.splitter.addWidget(self.text_browser)

        try:
            self.splitter.restoreState(QByteArray.fromHex(bytes(config['splitter_state'], 'ascii')))

        except Exception as e:
            logger.info('未发现splitter状态, 使用默认分隔比例')
            self.splitter.setStretchFactor(0, 8)
            self.splitter.setStretchFactor(1, 1)

        # 实时预览
        # self.splitter.setOpaqueResize(False)
        self.layout.addWidget(self.splitter)
        self.setLayout(self.layout)
        # 居中显示
        self.center()
        self.preventHeaderResizeEvent = False
        self.show()

    def custom_text_browser_resize_event(self, event):
        # 文本框大小变化时, 记录splitter的状态
        logger.info(f"custom_resize_event {self.height, self.tableWidget.height(), self.text_browser.height()}")
        logger.info(f"splitter_state {self.splitter.saveState()}")
        config['splitter_state'] = bytes(self.splitter.saveState().toHex()).decode('ascii')
        save_config(update_data=False)

    def createButton(self):
        self.output_button = QPushButton('生成RSS订阅下载规则', self)
        self.output_button.setToolTip('生成RSS订阅下载规则')
        self.output_button.clicked.connect(self.on_export_click)

        self.move_up_button = QPushButton('向上移动', self)
        self.move_up_button.clicked.connect(self.on_move_up_click)
        self.move_down_button = QPushButton('向下移动', self)
        self.move_down_button.clicked.connect(self.on_move_down_click)

        self.load_config_button = QPushButton('恢复上一次保存配置', self)
        self.load_config_button.clicked.connect(self.on_load_config_click)

        self.save_button = QPushButton('保存配置', self)
        self.save_button.clicked.connect(self.on_save_click)

        self.clean_row_button = QPushButton('清理空行', self)
        self.clean_row_button.clicked.connect(self.on_clean_row_click)

        self.backup_button = QPushButton('备份配置', self)
        self.backup_button.clicked.connect(self.on_backup_click)

    def createTable(self):
        self.tableWidget = QTableWidget()
        # 行数
        self.tableWidget.setRowCount(len(data_list))
        # 列数
        self.tableWidget.setColumnCount(len(headers))

        # 垂直表头修改
        # 文字居中显示
        self.tableWidget.verticalHeader().setStyleSheet("QHeaderView { qproperty-defaultAlignment: AlignCenter; }")

        # 渲染表头
        self.preventHeaderResizeEvent = True
        for i, x in enumerate(headers):
            item = QTableWidgetItem(x)
            item.setForeground(QtGui.QColor(0, 0, 255))
            self.tableWidget.setHorizontalHeaderItem(i, item)
        self.tableWidget.horizontalHeader().sectionResized.connect(self.on_header_resized)

        # 渲染数据
        # 空数据处理
        if not data_list:
            for x in range(len(headers)):
                self.tableWidget.setItem(0, x, QTableWidgetItem(""))
        else:
            for cx, row in enumerate(data_list):
                for cy, d in enumerate(row):
                    item = QTableWidgetItem(d)
                    if cy in config['center_columns']:
                        item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.setItem(cx, cy, item)

        self.tableWidget.move(0, 0)

        # 宽度自适应 效果不太好
        # self.tableWidget.resizeColumnsToContents()
        # self.tableWidget.resizeColumnsToContents()
        # 拉长
        header = self.tableWidget.horizontalHeader()
        # header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)

        # self.tableWidget.setColumnWidth(0, 80)
        # self.tableWidget.setColumnWidth(1, 260)
        # self.tableWidget.setColumnWidth(2, 210)
        # self.tableWidget.setColumnWidth(3, 65)
        # self.tableWidget.setColumnWidth(4, 62)
        # self.tableWidget.setColumnWidth(5, 370)
        # self.tableWidget.setColumnWidth(6, 290)

        for i in range(len(headers)):
            self.tableWidget.setColumnWidth(i, config['column_width_list'][i])

        # 双击事件绑定
        self.tableWidget.doubleClicked.connect(self.on_double_click)

        # 修改事件绑定
        self.tableWidget.cellChanged.connect(self.on_cell_changed)

        self.tableWidget.keyPressEvent = self.handle_key_press

        # 表格 右键菜单
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.generateMenu)
        # 表格 滚动条去掉右键菜单
        self.tableWidget.verticalScrollBar().setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.tableWidget.horizontalScrollBar().setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        logger.info('delegate 初始化')
        # 自定义处理
        self.tableWidget.setItemDelegateForColumn(2, CustomDelegate(self))
        self.tableWidget.setItemDelegateForColumn(3, CustomDelegate(self))

    def generateTextBrowserMenu(self, pos):
        """文本框自定义右键菜单"""
        time.sleep(0)
        logger.info(f"pos: {pos.x(), pos.y()}")
        a = QPoint(pos.x(), pos.y())

        self.text_browser_menu = QMenu(self)

        self.copy_text_action = QAction("复制")
        self.select_all_action = QAction("全选")

        self.copy_text_action.triggered.connect(self.on_copy_text_click)
        self.select_all_action.triggered.connect(self.on_select_all_click)

        self.text_browser_menu.addAction(self.copy_text_action)
        self.text_browser_menu.addAction(self.select_all_action)

        self.text_browser_menu.exec_(self.text_browser.mapToGlobal(a))

    def on_copy_text_click(self):
        """文本框右键菜单 复制 按钮事件"""
        logger.info('on_copy_text_click()')
        self.text_browser.copy()

    def on_select_all_click(self):
        """文本框右键菜单 全选 按钮事件"""
        logger.info('on_select_all_click()')
        self.text_browser.selectAll()

    def generateMenu(self, pos):
        # 右键弹窗菜单
        # 右键弹窗菜单加一个sleep, 防止长按右键导致右键事件被重复触发
        time.sleep(0)
        # 感觉弹出菜单和实际鼠标点击位置有偏差, 尝试手动修正
        logger.info(f"pos {pos.x(), pos.y()}")
        a = QPoint(pos.x() + 26, pos.y() + 22)

        self.menu = QMenu(self)
        self.up_action = QAction("向上移动")
        self.down_action = QAction("向下移动")
        self.delete_action = QAction("删除整条订阅")
        self.clear_action = QAction("清理空行")

        self.up_action.triggered.connect(self.on_move_up_click)
        self.down_action.triggered.connect(self.on_move_down_click)
        self.delete_action.triggered.connect(self.menu_delete_action)
        self.clear_action.triggered.connect(self.on_clean_row_click)

        self.menu.addAction(self.up_action)
        self.menu.addAction(self.down_action)
        self.menu.addAction(self.delete_action)
        self.menu.addAction(self.clear_action)
        self.menu.exec_(self.tableWidget.mapToGlobal(a))
        # return

    def on_header_resized(self):
        if self.preventHeaderResizeEvent:
            return
        logger.info('on_header_resized()')
        # 修改列宽写入配置
        column_width_list_tmp = []
        for i in range(len(headers)):
            column_width_list_tmp.append(self.tableWidget.columnWidth(i))
        logger.info(column_width_list_tmp)
        config['column_width_list'] = column_width_list_tmp
        save_config(update_data=False)

    def load_type_hints(self, row):
        try:
            self.tableWidget.type_hints = []
            # 当前行feed路径数据
            current_row_feed = data_list[row][6]
            logger.info(f'current_row_feed {current_row_feed}')
            # 读取qb feed json数据
            feed_uid = None
            with open(config['feeds_json_path'], 'r', encoding='utf-8') as f:
                feeds_json = json.loads(f.read())
                logger.info(f'feeds_json {feeds_json}')
                for x in feeds_json:
                    if current_row_feed == feeds_json[x]['url']:
                        feed_uid = feeds_json[x]['uid'].replace('-', '')[1:-1]
                        logger.info(f'feed_uid {feed_uid}')
                        break
            if feed_uid:
                # 读取rss feed的标题 写入 type_hints 列表
                article_titles = []
                article_path = config['rss_article_folder'] + '/' + feed_uid + '.json'
                with open(article_path, 'r', encoding='utf-8') as f:
                    article = json.loads(f.read())
                    for x in article:
                        article_titles.append(x['title'])
                self.tableWidget.type_hints = article_titles
                logger.info(self.tableWidget.type_hints)
                return True
        except Exception as e:
            logger.info(f'exception {e}')
        self.text_browser.setText('没找到RSS数据呀')

    def do_search(self):
        """搜索框按钮事件"""
        logger.info('do_search()')
        # 搜索关键字
        # keyword = self.search_window.lineEdit.text()
        keyword = self.search_window.text_edit_list[self.search_window.last_tab].text()
        logger.info(keyword)
        if not keyword:
            return

        if self.search_window.last_search_keyword != keyword or self.search_window.last_data_update_timestamp != self.data_update_timestamp:
            logger.info('数据有变动, 重新搜索')
            self.text_browser.clear()
            self.last_search_index = 0
            self.search_window.search_result = []
            # 目标
            selected_columns = list(range(len(headers)))
            for r in range(len(data_list)):
                for c in selected_columns:
                    cell_data = data_list[r][c]
                    # 忽略大小写
                    if keyword.lower() in cell_data.lower():
                        logger.info(f'找到了! {r, c, cell_data}')
                        self.search_window.search_result.append({'r': r, 'c': c, 'cell_data': cell_data})
            self.search_window.last_search_keyword = keyword
            # 如果有匹配的结果, 进行跳转
            if self.search_window.search_result:
                self.search_window.last_data_update_timestamp = self.data_update_timestamp
        else:
            logger.info('继续遍历上次搜索的结果')
            self.last_search_index = (self.last_search_index + 1) % len(self.search_window.search_result)

        if self.search_window.search_result:
            logger.info(
                f"跳转 {self.search_window.search_result[self.last_search_index]['r'], self.search_window.search_result[self.last_search_index]['c']}")
            self.tableWidget.setCurrentCell(self.search_window.search_result[self.last_search_index]['r'],
                                            self.search_window.search_result[self.last_search_index]['c'])
            self.text_browser.setText(f'搜索结果: {self.last_search_index + 1}/{len(self.search_window.search_result)}')
            self.activateWindow()
        else:
            self.text_browser.setText('没有找到匹配的数据')

    def search_tab_change(self, index):
        logger.info(f'search_tab_change() {index}')
        if self.search_window.last_tab != index:
            self.search_window.text_edit_list[index].setText(
                self.search_window.text_edit_list[self.search_window.last_tab].text())
        self.search_window.last_tab = index

    def do_replace(self):
        logger.info(f'do_replace() 替换当前单元格内容')
        source_text = self.search_window.text_edit_list[self.search_window.last_tab].text()
        if not source_text:
            return
        target_text = self.search_window.lineEditReplaceTarget.text()
        logger.info(f'{source_text} 替换为 {target_text}')
        pat = re.compile(re.escape(source_text), re.IGNORECASE)
        result = pat.sub(target_text, self.tableWidget.currentItem().text())
        logger.info(result)
        self.tableWidget.currentItem().setText(result)
        self.do_search()

    def do_replace_all(self):
        logger.info(f'do_replace_all() 替换全部单元格内容')
        source_text = self.search_window.text_edit_list[self.search_window.last_tab].text()
        if not source_text:
            return
        target_text = self.search_window.lineEditReplaceTarget.text()
        logger.info(f'{source_text} 替换为 {target_text}')
        pat = re.compile(re.escape(source_text), re.IGNORECASE)

        self.tableWidget.blockSignals(True)
        data_list = clean_data_list()
        # 长度补充
        if len(data_list) < config['max_row_size']:
            for _ in range(config['max_row_size'] - len(data_list)):
                data_list.append(['' for x in range(len(headers))])
        # 更新整个列表
        for cx, row in enumerate(data_list):
            for cy, d in enumerate(row):
                # 替换数据
                d = pat.sub(target_text, d)
                item = QTableWidgetItem(d)
                if cy in config['center_columns']:
                    item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(cx, cy, item)

        self.tableWidget.blockSignals(False)

    def show_message(self, message, title):
        """弹出框消息"""
        self.msg = QMessageBox()
        # 设置图标
        self.msg.setWindowIcon(QtGui.QIcon(resource_path('QBRssManager.ico')))
        # 只能通过设置样式来修改宽度, 其它设置没用
        self.msg.setStyleSheet("QLabel {min-width: 70px;}")
        # 提示信息
        self.msg.setText(message)
        # 标题
        self.msg.setWindowTitle(title)
        self.msg.show()

    @pyqtSlot()
    def on_double_click(self):
        # 双击事件
        logger.info("on_double_click()")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            logger.info(
                f'{currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text()}')

            # 读取feed数据 用于过滤输入
            if (currentQTableWidgetItem.column() in (2, 3)):
                self.text_browser.clear()
                res = self.load_type_hints(currentQTableWidgetItem.row())
                if res:
                    self.text_browser.filter_type_hint()

    @pyqtSlot()
    def on_move_up_click(self):
        logger.info('on_move_up_click()')
        # 上移事件
        # 防止触发 cellChange 事件导致重复更新
        self.tableWidget.blockSignals(True)
        r = self.tableWidget.currentRow()
        c = self.tableWidget.currentColumn()
        logger.info(f'{r, c}')
        # 未选中任何单元格时 坐标是 (-1, -1)
        if r == 0 or r == -1:
            return

        data_list[r], data_list[r - 1] = data_list[r - 1], data_list[r]

        for i in range(len(headers)):
            item1 = QTableWidgetItem(data_list[r][i])
            item2 = QTableWidgetItem(data_list[r - 1][i])
            if i in config['center_columns']:
                item1.setTextAlignment(Qt.AlignCenter)
                item2.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(r, i, item1)
            self.tableWidget.setItem(r - 1, i, item2)

        self.tableWidget.setCurrentCell(r - 1, c)
        if config['auto_save']:
            save_config()
        self.tableWidget.blockSignals(False)

    @pyqtSlot()
    def on_move_down_click(self):
        # 下移事件
        # 防止触发 cellChange 事件导致重复更新
        self.tableWidget.blockSignals(True)
        r = self.tableWidget.currentRow()
        c = self.tableWidget.currentColumn()
        logger.info(f'{r, c}')
        if r == len(data_list) or r == -1:
            return

        data_list[r], data_list[r + 1] = data_list[r + 1], data_list[r]

        for i in range(len(headers)):
            item1 = QTableWidgetItem(data_list[r][i])
            item2 = QTableWidgetItem(data_list[r + 1][i])
            if i in config['center_columns']:
                item1.setTextAlignment(Qt.AlignCenter)
                item2.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(r, i, item1)
            self.tableWidget.setItem(r + 1, i, item2)

        self.tableWidget.setCurrentCell(r + 1, c)
        if config['auto_save']:
            save_config()
        self.tableWidget.blockSignals(False)

    @pyqtSlot()
    def on_cell_changed(self):
        logger.info('on_cell_changed()')
        # 修改事件
        r = self.tableWidget.currentRow()
        c = self.tableWidget.currentColumn()
        text = self.tableWidget.currentItem().text()
        logger.info(f'{r, c, text}')

        # 第一列时间进行特殊转换处理
        if c == 0:
            text = try_convert_time(text)
            self.tableWidget.currentItem().setText(text)

        # 修改数据
        data_list[r][c] = text
        logger.info(f'on_cell_changed 结果 {data_list}')
        if config['auto_save']:
            save_config()

        # 记录数据修改的时间作为简易版本号, 用来标记搜索结果是否要更新
        self.data_update_timestamp = int(datetime.now().timestamp() * 1000)

    @pyqtSlot()
    def on_export_click(self):
        logger.info('生成qb订阅规则')

        # 检查端口可用性
        port_open = False
        if config['use_qb_api'] == 1:
            a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            location = (config['qb_api_ip'], int(config['qb_api_port']))
            result_of_check = a_socket.connect_ex(location)
            if result_of_check == 0:
                port_open = True
            else:
                port_open = False

        if config['use_qb_api'] == 1 and port_open:
            # 使用qb的api, 可以不重启qb
            try:
                qb_client.auth_log_in()
            except qbittorrentapi.LoginFailed as e:
                logger.error(e)

            # 清空已有规则
            rss_rules = qb_client.rss_rules()
            for x in rss_rules:
                print(x)
                qb_client.rss_remove_rule(x)
            # 添加新规则
            for x in clean_data_list():
                qb_client.rss_set_rule(
                    rule_name=x[0] + ' ' + x[1],
                    rule_def={
                        "enabled": True,
                        "mustContain": x[2],
                        "mustNotContain": x[3],
                        "savePath": format_path(x[5]),
                        "affectedFeeds": [x[6], ],
                        "assignedCategory": x[7]
                    }
                )
            subprocess.Popen([config['qb_executable']])
        else:
            # 不使用qb的api, 需要重启qb
            output_data = {}
            for x in clean_data_list():
                logger.info(x)
                item = {
                    "enabled": True,
                    "mustContain": x[2],
                    "mustNotContain": x[3],
                    "savePath": format_path(x[5]),
                    "affectedFeeds": [x[6], ],
                    "assignedCategory": x[7]
                }

                output_data[x[0] + ' ' + x[1]] = item
            logger.info(config['rules_path'])
            with open(config['rules_path'], 'w', encoding='utf-8') as f:
                f.write(json.dumps(output_data, ensure_ascii=False))
            logger.info(config['open_qb_after_export'])
            if config['open_qb_after_export']:
                # 关闭qb
                try:
                    os.system(f'taskkill /f /im {qb_executable_name}')
                except:
                    pass
                # 启动qb
                subprocess.Popen([config['qb_executable']])
                # 刷新任务栏托盘图标
                refresh_tray()

    @pyqtSlot()
    def on_load_config_click(self):
        self.tableWidget.blockSignals(True)
        # 这里要覆盖变量
        global config
        global data_list
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.loads(f.read())
            data_list = config['data_list'][::]
            if len(data_list) < config['max_row_size']:
                for _ in range(config['max_row_size'] - len(data_list)):
                    data_list.append(['' for x in range(len(headers))])
            # 重新渲染数据
            for cx, row in enumerate(data_list):
                for cy, d in enumerate(row):
                    item = QTableWidgetItem(d)
                    if cy in config['center_columns']:
                        item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.setItem(cx, cy, item)
        self.tableWidget.blockSignals(False)

    @pyqtSlot()
    def on_save_click(self):
        config['full_window_width'] = self.normalGeometry().width()
        config['full_window_height'] = self.normalGeometry().height()
        column_width_list_tmp = []
        for i in range(len(headers)):
            column_width_list_tmp.append(self.tableWidget.columnWidth(i))
        config['column_width_list'] = column_width_list_tmp
        save_config()
        self.show_message("保存成功", "不错不错")

    @pyqtSlot()
    def on_clean_row_click(self):
        # 防止触发 cellChange 事件导致重复更新
        self.tableWidget.blockSignals(True)
        data_list = clean_data_list()
        # 长度补充
        if len(data_list) < config['max_row_size']:
            for _ in range(config['max_row_size'] - len(data_list)):
                data_list.append(['' for x in range(len(headers))])
        # 更新整个列表
        for cx, row in enumerate(data_list):
            for cy, d in enumerate(row):
                item = QTableWidgetItem(d)
                if cy in config['center_columns']:
                    item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(cx, cy, item)

        self.tableWidget.blockSignals(False)

    @pyqtSlot()
    def on_backup_click(self):
        """备份配置"""
        # 先保存再备份
        save_config()
        logger.info('备份')
        backup_file_name = f'config_{datetime.now()}.json'
        logger.info(backup_file_name)
        zip_obj = ZipFile('backup.zip', 'a')
        zip_obj.write('config.json', backup_file_name)
        logger.info('备份完成')
        self.show_message('备份完成', '不怕手抖')

    def handle_key_press(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_F2):
            logger.info('edit cell')
            # PyQt5.QtCore.QModelIndex
            currentQTableWidgetItem = self.tableWidget.currentItem()
            logger.info(
                f'{currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text()}')
            # 读取feed数据 用于过滤输入
            if (currentQTableWidgetItem.column() in (2, 3)):
                self.text_browser.clear()
                res = self.load_type_hints(currentQTableWidgetItem.row())
                if res:
                    self.text_browser.filter_type_hint()

            self.tableWidget.edit(self.tableWidget.currentIndex())

        #   复制粘贴
        elif event.key() == Qt.Key_C and (event.modifiers() & Qt.ControlModifier):
            logger.info('ctrl c')
            self.copied_cells = sorted(self.tableWidget.selectedIndexes())
            logger.info(f'复制了 {len(self.copied_cells)} 个')

            # 清空剪贴板
            # app.clipboard().setText('')

            # 尝试构造 excel 格式数据
            if len(self.copied_cells) > 0:
                # 找出输出区域坐标
                min_row = self.copied_cells[0].row()
                max_row = self.copied_cells[0].row()
                min_col = self.copied_cells[0].column()
                max_col = self.copied_cells[0].column()

                for cell in self.copied_cells:
                    min_row = min(min_row, cell.row())
                    max_row = max(max_row, cell.row())
                    min_col = min(min_col, cell.column())
                    max_col = max(max_col, cell.column())

                logger.info(f'{min_row} {max_row} {min_col} {max_col}')

                tmp_row_count = max_row - min_row + 1
                tmp_col_count = max_col - min_col + 1

                # 构造输出文本
                tmp_list = [["" for x in range(tmp_col_count)] for y in range(tmp_row_count)]

                for cell in self.copied_cells:
                    tmp_list[cell.row() - min_row][cell.column() - min_col] = cell.data()

                # excel 列数据以\t分隔 行数据以\n分隔
                lines = []
                for r in tmp_list:
                    line = '\t'.join(r)
                    lines.append(line)
                excel_text = '\n'.join(lines)
                app.clipboard().setText(excel_text)

        elif event.key() == Qt.Key_V and (event.modifiers() & Qt.ControlModifier):
            logger.info('ctrl v')
            self.tableWidget.blockSignals(True)

            # 如果剪贴板有内容 优先粘贴剪贴板
            # 可以兼容excel表格的复制粘贴
            if app.clipboard().text():
                logger.info('导入excel')
                r = self.tableWidget.currentRow()
                c = self.tableWidget.currentColumn()
                rows = app.clipboard().text().split('\n')
                for b_r, row in enumerate(rows):
                    if not row:
                        continue
                    cells = row.split('\t')
                    logger.info(cells)

                    for b_c, cell_data in enumerate(cells):
                        new_r = b_r + r
                        new_c = b_c + c
                        if new_c > (len(headers) - 1):
                            # 忽略跨行数据 防止数组越界
                            continue
                        logger.info(f'粘贴数据 {new_r, new_c, cell_data}')
                        item = QTableWidgetItem(cell_data)
                        if new_c in config['center_columns']:
                            item.setTextAlignment(Qt.AlignCenter)

                        self.tableWidget.setItem(new_r, new_c, item)
                        data_list[new_r][new_c] = cell_data
                        logger.info(f'粘贴结果 {data_list}')
                    # 保存结果
                    if config['auto_save']:
                        save_config()
                # app.clipboard().setText('')
                self.tableWidget.blockSignals(False)
                return
            else:
                # 复制增加了剪贴板写入 这个分支可能已经不会触发了 以后考虑删除
                if not self.copied_cells:
                    return
                r = self.tableWidget.currentRow() - self.copied_cells[0].row()
                c = self.tableWidget.currentColumn() - self.copied_cells[0].column()
                logger.info(f'准备粘贴 {len(self.copied_cells)} 个')
                for cell in self.copied_cells:
                    new_r = cell.row() + r
                    new_c = cell.column() + c
                    if new_c > (len(headers) - 1):
                        # 忽略跨行数据 防止数组越界
                        continue
                    logger.info(f'粘贴数据 {new_r, new_c, cell.data()}')
                    item = QTableWidgetItem(cell.data())
                    if new_c in config['center_columns']:
                        item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.setItem(new_r, new_c, item)
                    data_list[new_r][new_c] = cell.data()
                    logger.info(f'粘贴结果 {data_list}')
                # 保存结果
                if config['auto_save']:
                    save_config()
                self.tableWidget.blockSignals(False)

        # 搜索
        elif event.key() == Qt.Key_F and (event.modifiers() & Qt.ControlModifier):
            logger.info('ctrl f')
            pos = self.search_window.pos()
            logger.info(f'self.search_window {pos.x(), pos.y()}')
            self.search_window.tabs.setCurrentIndex(0)
            self.search_window.show()
            # 获取焦点
            self.search_window.activateWindow()

        # 替换
        elif event.key() == Qt.Key_H and (event.modifiers() & Qt.ControlModifier):
            logger.info('ctrl h')
            pos = self.search_window.pos()
            logger.info(f'self.search_window {pos.x(), pos.y()}')
            self.search_window.tabs.setCurrentIndex(1)
            self.search_window.show()
            # 获取焦点
            self.search_window.activateWindow()

        # 删除数据
        elif event.key() == Qt.Key_Delete:
            logger.info('delete')
            self.tableWidget.blockSignals(True)
            for x in self.tableWidget.selectedIndexes():
                r = x.row()
                c = x.column()
                self.tableWidget.setItem(r, c, QTableWidgetItem(""))
                data_list[r][c] = ""
            if config['auto_save']:
                save_config()
            self.tableWidget.blockSignals(False)

        # 方向键
        elif event.key() == Qt.Key_Right:
            logger.info('Move right')
            self.tableWidget.setCurrentCell(self.tableWidget.currentRow(),
                                            min(self.tableWidget.currentColumn() + 1, len(headers) - 1))
        elif event.key() == Qt.Key_Left:
            logger.info('Move left')
            self.tableWidget.setCurrentCell(self.tableWidget.currentRow(),
                                            max(self.tableWidget.currentColumn() - 1, 0))
        elif event.key() == Qt.Key_Up:
            logger.info('Move up')
            self.tableWidget.setCurrentCell(max(self.tableWidget.currentRow() - 1, 0),
                                            self.tableWidget.currentColumn())
        elif event.key() == Qt.Key_Down:
            logger.info('Move down')
            self.tableWidget.setCurrentCell(max(self.tableWidget.currentRow() + 1, 0),
                                            self.tableWidget.currentColumn())

        elif event.key() == Qt.Key_I and (event.modifiers() & Qt.ControlModifier):
            # 导入excel数据
            logger.info('ctrl i')
            self.tableWidget.blockSignals(True)
            r = self.tableWidget.currentRow()
            c = self.tableWidget.currentColumn()
            rows = app.clipboard().text().split('\n')
            for b_r, row in enumerate(rows):
                if not row:
                    continue
                cells = row.split('\t')
                logger.info(cells)

                for b_c, cell_data in enumerate(cells):
                    new_r = b_r + r
                    new_c = b_c + c
                    if new_c > (len(headers) - 1):
                        # 忽略跨行数据 防止数组越界
                        continue
                    logger.info(f'粘贴数据 {new_r, new_c, cell_data}')
                    self.tableWidget.setItem(new_r, new_c, QTableWidgetItem(cell_data))
                    data_list[new_r][new_c] = cell_data
                    logger.info(f'粘贴结果 {data_list}')
                # 保存结果
                if config['auto_save']:
                    save_config()
            self.tableWidget.blockSignals(False)
        elif event.key() in (Qt.Key_F3,):
            self.do_search()

        elif event.key() in (Qt.Key_Escape,):
            if self.search_window and self.search_window.isVisible():
                self.search_window.close()

    # return

    def menu_delete_action(self):
        # 右键菜单 删除
        r = self.tableWidget.currentRow()
        logger.info(r)
        self.tableWidget.blockSignals(True)

        # 修改为只删除当前行, 不清理列表
        r = self.tableWidget.currentRow()
        data_list[r] = ['' for _ in range(len(headers))]
        cx = r
        for cy in range(len(headers)):
            item = QTableWidgetItem('')
            if cy in config['center_columns']:
                item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(cx, cy, item)

        self.tableWidget.blockSignals(False)

    def resizeEvent(self, event):
        logger.info("Window has been resized")
        config['full_window_width'] = self.normalGeometry().width()
        config['full_window_height'] = self.normalGeometry().height()
        save_config(update_data=False)

    def closeEvent(self, event):
        # 主窗口的关闭按钮事件
        if config['close_to_tray']:
            logger.info('关闭按钮最小化到任务栏托盘')
            self.hide()
            self.tray_icon.show()
            event.ignore()
        else:
            sys.exit()


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


def refresh_tray():
    logger.info('刷新任务栏托盘图标')
    # 刷新任务栏托盘图标, 去掉强制关闭进程后的残留图标
    hShellTrayWnd = win32gui.FindWindow("Shell_trayWnd", "")
    hTrayNotifyWnd = win32gui.FindWindowEx(hShellTrayWnd, 0, "TrayNotifyWnd", None)
    hSysPager = win32gui.FindWindowEx(hTrayNotifyWnd, 0, 'SysPager', None)
    if hSysPager:
        hToolbarWindow32 = win32gui.FindWindowEx(hSysPager, 0, 'ToolbarWindow32', None)
    else:
        hToolbarWindow32 = win32gui.FindWindowEx(hTrayNotifyWnd, 0, 'ToolbarWindow32', None)
    logger.info(f'hToolbarWindow32 {hToolbarWindow32}')
    if hToolbarWindow32:
        rect = win32gui.GetWindowRect(hToolbarWindow32)
        logger.info(rect)
        # 窗口宽度 // 图标宽度 = 图标个数?
        for x in range((rect[2] - rect[0]) // 24):
            win32gui.SendMessage(hToolbarWindow32, WM_MOUSEMOVE, 0, 1)


def resource_path(relative_path):
    # 兼容pyinstaller的文件资源访问
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


# 获取pyqt5的exception
def catch_exceptions(t, val, tb):
    QtWidgets.QMessageBox.critical(None,
                                   "An exception was raised",
                                   "Exception type: {}".format(t))
    old_hook(t, val, tb)


old_hook = sys.excepthook
sys.excepthook = catch_exceptions

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 加上这个表头才有样式
    app.setStyle(QStyleFactory.create('Fusion'))
    ex = App()
    sys.exit(app.exec_())
