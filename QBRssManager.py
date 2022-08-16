import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from zipfile import ZipFile

import qbittorrentapi
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import pyqtSlot, Qt, QPoint, QByteArray
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QDesktopWidget, \
    QStyleFactory, QPushButton, QHBoxLayout, QMessageBox, QMenu, QAction, QSplitter, \
    QFileDialog, QTabWidget
from loguru import logger

import g
from g import save_config, clean_data_list, headers
from ui.custom_delegate import CustomDelegate
from ui.custom_qtext_browser import CustomQTextBrowser
from ui.search_window import SearchWindow
from ui.tray_icon import TrayIcon
from utils.path_util import resource_path, format_path_by_system, format_path
from utils.pyqt_util import catch_exceptions
from utils.qb_util import check_qb_port_open
from utils.string_util import try_split_date_and_name
from utils.time_util import try_convert_time
from utils.windows_util import refresh_tray

g.config, g.data_list = g.init_config()

# 初始化qb_api客户端
if g.config['use_qb_api']:
    qb_client = qbittorrentapi.Client(
        host=g.config['qb_api_ip'],
        port=g.config['qb_api_port'],
        VERIFY_WEBUI_CERTIFICATE=False,
    )


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'qBittorrent 订阅下载规则管理 v1.2.3 by Nriver'
        # 图标
        self.setWindowIcon(QtGui.QIcon(resource_path('QBRssManager.ico')))
        self.left = 0
        self.top = 0
        self.width = g.config['full_window_width']
        self.height = g.config['full_window_height']
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
        self.tableWidget_list = [QTableWidget() for _ in range(len(g.data_groups))]
        self.createTable()
        self.layout_button = QHBoxLayout()
        self.layout_button.addWidget(self.move_up_button)
        self.layout_button.addWidget(self.move_down_button)
        self.layout_button.addWidget(self.clean_row_button)
        self.layout_button.addWidget(self.load_config_button)
        self.layout_button.addWidget(self.save_button)
        self.layout_button.addWidget(self.backup_button)
        self.layout_button.addWidget(self.output_button)

        # 无法共享widget 只好初始化多个widget了
        self.tab = QTabWidget()
        for i, x in enumerate(self.tableWidget_list):
            self.tab.addTab(x, g.data_groups[i]['name'])
        self.tab.currentChanged.connect(self.on_tab_changed)

        # 文本框 固定位置方便输出
        self.text_browser = CustomQTextBrowser(self)
        self.text_browser.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        # self.text_browser.setMaximumHeight(g.config['text_browser_height'])

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
        # self.splitter.addWidget(self.tableWidget)
        self.splitter.addWidget(self.tab)
        self.splitter.addWidget(self.text_browser)

        try:
            self.splitter.restoreState(QByteArray.fromHex(bytes(g.config['splitter_state'], 'ascii')))

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
        g.config['splitter_state'] = bytes(self.splitter.saveState().toHex()).decode('ascii')
        save_config(update_data=False)

    def createButton(self):
        self.output_button = QPushButton('生成RSS订阅下载规则', self)
        self.output_button.setToolTip('生成RSS订阅下载规则')
        self.output_button.clicked.connect(self.on_export_click)

        self.move_up_button = QPushButton('向上移动', self)
        self.move_up_button.clicked.connect(self.on_move_up_click)
        self.move_down_button = QPushButton('向下移动', self)
        self.move_down_button.clicked.connect(self.on_move_down_click)

        self.load_config_button = QPushButton('恢复上一次保存的配置', self)
        self.load_config_button.clicked.connect(self.on_load_config_click)

        self.save_button = QPushButton('保存配置', self)
        self.save_button.clicked.connect(self.on_save_click)

        self.clean_row_button = QPushButton('清理空行', self)
        self.clean_row_button.clicked.connect(self.on_clean_row_click)

        self.backup_button = QPushButton('备份配置', self)
        self.backup_button.clicked.connect(self.on_backup_click)

    def createTable(self):
        self.tableWidget = self.tableWidget_list[g.current_data_list_index]
        # 行数
        self.tableWidget.setRowCount(len(g.data_list))
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
        if not g.data_list:
            for x in range(len(headers)):
                self.tableWidget.setItem(0, x, QTableWidgetItem(""))
        else:
            for cx, row in enumerate(g.data_list):
                for cy, d in enumerate(row):
                    item = QTableWidgetItem(d)
                    if cy in g.config['center_columns']:
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
            self.tableWidget.setColumnWidth(i, g.config['column_width_list'][i])

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
        self.delete_all_action = QAction("删除所有订阅")
        self.clear_action = QAction("清理空行")
        self.load_config_action = QAction("恢复上一次保存的配置")
        self.import_exist_qb_rule_action = QAction("从qb导入已有规则")
        self.import_from_share_file_action = QAction("从分享文件导入规则")
        self.export_to_share_file_action = QAction("导出规则到文件进行分享")

        self.up_action.triggered.connect(self.on_move_up_click)
        self.down_action.triggered.connect(self.on_move_down_click)
        self.delete_action.triggered.connect(self.menu_delete_action)
        self.delete_all_action.triggered.connect(self.menu_delete_all_action)
        self.clear_action.triggered.connect(self.on_clean_row_click)
        self.load_config_action.triggered.connect(self.on_load_config_click)
        self.import_exist_qb_rule_action.triggered.connect(self.on_import_exist_qb_rule_action)
        self.import_from_share_file_action.triggered.connect(self.on_import_from_share_file_action)
        self.export_to_share_file_action.triggered.connect(self.on_export_to_share_file_action)

        self.menu.addAction(self.up_action)
        self.menu.addAction(self.down_action)
        self.menu.addSeparator()
        self.menu.addAction(self.delete_action)
        self.menu.addAction(self.delete_all_action)
        self.menu.addAction(self.clear_action)
        self.menu.addSeparator()
        self.menu.addAction(self.load_config_action)
        self.menu.addAction(self.import_exist_qb_rule_action)
        self.menu.addSeparator()
        self.menu.addAction(self.import_from_share_file_action)
        self.menu.addAction(self.export_to_share_file_action)

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
        g.config['column_width_list'] = column_width_list_tmp
        save_config(update_data=False)

    def load_type_hints(self, row):
        # 输入过程中实时过滤数据
        self.tableWidget.type_hints = []
        # 当前行feed路径数据
        current_row_feed = g.data_list[row][6]
        logger.info(f'current_row_feed {current_row_feed}')

        if g.config['use_qb_api'] == 1 and check_qb_port_open(g.config['qb_api_ip'], g.config['qb_api_port']):
            # 使用qb的api读取feed
            try:
                qb_client.auth_log_in(username=g.config['qb_api_username'], password=g.config['qb_api_password'])
                self.text_browser.append('通过api获取feed')
                rss_feeds = qb_client.rss_items(include_feed_data=True)
                article_titles = []
                for x in rss_feeds:
                    if current_row_feed == rss_feeds[x]['url']:
                        for article in rss_feeds[x]['articles']:
                            article_titles.append(article['title'])
                self.tableWidget.type_hints = article_titles
                logger.info(self.tableWidget.type_hints)
                return True

            # except qbittorrentapi.LoginFailed as e:
            #     self.text_browser.append('api登录失败')
            #     self.text_browser.append(e)
            except Exception as e:
                logger.error(e)
                self.text_browser.append('通过api连接qb失败')
                self.text_browser.append(f'报错信息 {repr(e)}')
        else:
            # 读取本地feed文件
            try:
                # 读取qb feed json数据
                feed_uid = None
                with open(g.config['feeds_json_path'], 'r', encoding='utf-8') as f:
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
                    article_path = g.config['rss_article_folder'] + '/' + feed_uid + '.json'
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
            for r in range(len(g.data_list)):
                for c in selected_columns:
                    cell_data = g.data_list[r][c]
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
        try:
            result = pat.sub(target_text, self.tableWidget.currentItem().text())
        except:
            result = self.tableWidget.currentItem().text().replace(source_text, target_text)
        logger.info(result)
        g.data_list[self.tableWidget.currentItem().row()][self.tableWidget.currentItem().column()] = result
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
        g.data_list = clean_data_list(g.data_list)
        # 长度补充
        if len(g.data_list) < g.config['max_row_size']:
            for _ in range(g.config['max_row_size'] - len(g.data_list)):
                g.data_list.append(['' for x in range(len(headers))])
        # 更新整个列表
        for cx, row in enumerate(g.data_list):
            for cy, d in enumerate(row):
                # 替换数据
                try:
                    d = pat.sub(target_text, d)
                except:
                    d = d.replace(source_text, target_text)
                item = QTableWidgetItem(d)
                if cy in g.config['center_columns']:
                    item.setTextAlignment(Qt.AlignCenter)
                # 注意这里要更新g.data_list的数据
                g.data_list[cx][cy] = d
                self.tableWidget.setItem(cx, cy, item)

        self.tableWidget.blockSignals(False)

    def show_message(self, message, title):
        """弹出框消息"""
        self.msg = QMessageBox()
        # 设置图标
        self.msg.setWindowIcon(QtGui.QIcon(resource_path('QBRssManager.ico')))
        # 只能通过设置样式来修改宽度, 其它设置没用
        self.msg.setStyleSheet("QLabel {min-width: 80px;}")
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

        g.data_list[r], g.data_list[r - 1] = g.data_list[r - 1], g.data_list[r]

        for i in range(len(headers)):
            item1 = QTableWidgetItem(g.data_list[r][i])
            item2 = QTableWidgetItem(g.data_list[r - 1][i])
            if i in g.config['center_columns']:
                item1.setTextAlignment(Qt.AlignCenter)
                item2.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(r, i, item1)
            self.tableWidget.setItem(r - 1, i, item2)

        self.tableWidget.setCurrentCell(r - 1, c)

        # 更新数据
        g.update_data_list()

        if g.config['auto_save']:
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
        if r == len(g.data_list) or r == -1:
            return

        g.data_list[r], g.data_list[r + 1] = g.data_list[r + 1], g.data_list[r]

        for i in range(len(headers)):
            item1 = QTableWidgetItem(g.data_list[r][i])
            item2 = QTableWidgetItem(g.data_list[r + 1][i])
            if i in g.config['center_columns']:
                item1.setTextAlignment(Qt.AlignCenter)
                item2.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(r, i, item1)
            self.tableWidget.setItem(r + 1, i, item2)

        self.tableWidget.setCurrentCell(r + 1, c)

        # 更新数据
        g.update_data_list()

        if g.config['auto_save']:
            save_config()
        self.tableWidget.blockSignals(False)

    def on_tab_changed(self, index):
        """订阅分组tab切换"""
        logger.info(f'on_tab_changed() {index}')
        self.tableWidget.blockSignals(True)

        g.current_data_list_index = index
        logger.info('切换数据')
        g.parse_v1()
        logger.info('刷新表格')

        logger.info('清理表格绑定事件, 防止右键菜单多次触发')
        for x in self.tableWidget_list:
            try:
                # 如果没有绑定事件这里会抛异常，忽略就行
                x.customContextMenuRequested.disconnect()
            except:
                pass
        logger.info('切换表格')
        self.tableWidget = self.tableWidget_list[g.current_data_list_index]
        logger.info('创建表格 刷新界面')
        self.createTable()

        self.tableWidget.blockSignals(False)

    @pyqtSlot()
    def on_cell_changed(self):
        logger.info('on_cell_changed()')
        # 修改事件
        r = self.tableWidget.currentRow()
        c = self.tableWidget.currentColumn()
        current_item = self.tableWidget.currentItem()
        if not current_item:
            return
        text = self.tableWidget.currentItem().text()
        logger.info(f'{r, c, text}')

        # 第一列时间进行特殊转换处理
        if c == 0:
            text = try_convert_time(text, g.config['date_auto_zfill'])
            self.tableWidget.currentItem().setText(text)

        g.data_list[r][c] = text
        # 更新数据
        g.update_data_list()

        logger.info(f'on_cell_changed 结果 {g.data_list}')
        if g.config['auto_save']:
            save_config()

        # 记录数据修改的时间作为简易版本号, 用来标记搜索结果是否要更新
        self.data_update_timestamp = int(datetime.now().timestamp() * 1000)

    @pyqtSlot()
    def on_import_exist_qb_rule_action(self):
        logger.info('导入qb订阅规则')

        # 尝试通过api读取rss配置
        rss_rules = []

        self.text_browser.append('尝试通过api和qb通信')
        if g.config['use_qb_api'] == 1 and check_qb_port_open(g.config['qb_api_ip'], g.config['qb_api_port']):
            # 使用qb的api, 可以不重启qb
            try:
                qb_client.auth_log_in(username=g.config['qb_api_username'], password=g.config['qb_api_password'])
                self.text_browser.append('通过api获取已有规则')
                rss_rules = qb_client.rss_rules()
            # except qbittorrentapi.LoginFailed as e:
            #     self.text_browser.append('api登录失败')
            #     self.text_browser.append(e)
            except Exception as e:
                logger.error(e)
                self.text_browser.append('通过api连接qb失败')
                self.text_browser.append(f'报错信息 {repr(e)}')
        else:
            self.text_browser.append('无法通过qb的api获取rss数据')

        if not rss_rules:
            self.text_browser.append('尝试读取本机rss配置文件')
            try:
                with open(g.config['rules_path'], 'r', encoding='utf-8') as f:
                    rss_rules = json.loads(f.read())
            except:
                return

        self.text_browser.append('规则获取成功')

        # 对比表格内已有数据
        exist_data = {}
        for x in clean_data_list(g.data_list):
            item = {
                "enabled": True,
                "mustContain": x[2],
                "mustNotContain": x[3],
                "savePath": format_path_by_system(x[5]),
                "affectedFeeds": [x[6], ],
                "assignedCategory": x[7]
            }
            # 这里strip一下, 防止没有播出时间列匹配不到而重复导入
            exist_data[(x[0] + ' ' + x[1]).strip()] = item

        new_rules = []
        for x in rss_rules:
            if x in exist_data:
                if rss_rules[x] == exist_data[x]:
                    # logger.info('重复数据 跳过')
                    continue
                else:
                    # logger.info('===== 比较数据 begin =====')
                    # logger.info(f'规则 {rss_rules[x]}')
                    # logger.info('')
                    # logger.info(f'现存数据 {exist_data[x]}')
                    check_fields = ['mustContain', 'mustNotContain', 'savePath', 'affectedFeeds', 'assignedCategory']
                    for check_field in check_fields:
                        if rss_rules[x][check_field] != exist_data[x][check_field]:
                            new_rules.append(x)
                            continue
                    # logger.info('===== 比较数据 end =====')
            else:
                new_rules.append(x)
        logger.info(f'新数据 {len(new_rules)}')
        logger.info(new_rules)

        if not new_rules:
            return

        # 添加新数据 刷新表格
        self.tableWidget.blockSignals(True)
        g.data_list = clean_data_list(g.data_list)
        for x in new_rules:
            d = rss_rules[x]

            # 尝试分离日期
            release_date, series_name = try_split_date_and_name(x)

            g.data_list.append([
                release_date,
                series_name,
                d['mustContain'],
                d['mustNotContain'],
                '',
                format_path_by_system(d['savePath']),
                ','.join(d['affectedFeeds']),
                d['assignedCategory'],
            ])
        # 长度补充
        if len(g.data_list) < g.config['max_row_size']:
            for _ in range(g.config['max_row_size'] - len(g.data_list)):
                g.data_list.append(['' for x in range(len(headers))])
        # 更新整个列表
        for cx, row in enumerate(g.data_list):
            for cy, d in enumerate(row):
                item = QTableWidgetItem(d)
                if cy in g.config['center_columns']:
                    item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(cx, cy, item)
        # 更新数据
        g.update_data_list()
        # 保存结果
        if g.config['auto_save']:
            save_config()
        self.tableWidget.blockSignals(False)

    @pyqtSlot()
    def on_import_from_share_file_action(self):
        logger.info('从分享文件导入规则')
        file_info = QFileDialog.getOpenFileName(self, "选择文件", resource_path('.'), "json 文件(*.json)")
        share_file_path = file_info[0]
        logger.info(f'导入文件 {share_file_path}')

        if not share_file_path:
            # 没有选择文件时的异常处理
            return

        # 添加新数据 刷新表格
        self.tableWidget.blockSignals(True)

        with open(share_file_path, 'r', encoding='utf-8') as f:
            share_data = json.loads(f.read())
            # 旧版数据兼容，以后准备删除
            if 'version' not in share_data:
                logger.info('导入旧版共享数据')
                # 对比表格内已有数据
                g.data_list = clean_data_list(g.data_list)
                for x in share_data:
                    if x in g.data_list:
                        continue
                    g.data_list.append(x)
            elif share_data['version'] == 'v1':
                logger.info('导入 v1 数据')
                g.data_list = clean_data_list(g.data_list)
                if 'data_group' in share_data:
                    for x in share_data['data_group']['data']:
                        line = g.convert_v1_line(x)
                        if line in g.data_list:
                            continue
                        g.data_list.append(line)
            else:
                logger.info('未知格式的数据')
                return

            # 长度补充
            if len(g.data_list) < g.config['max_row_size']:
                for _ in range(g.config['max_row_size'] - len(g.data_list)):
                    g.data_list.append(['' for x in range(len(headers))])
            # 更新整个列表
            for cx, row in enumerate(g.data_list):
                for cy, d in enumerate(row):
                    item = QTableWidgetItem(d)
                    if cy in g.config['center_columns']:
                        item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.setItem(cx, cy, item)

            # 更新数据
            g.update_data_list()
            # 保存结果
            if g.config['auto_save']:
                save_config()

        self.tableWidget.blockSignals(False)

    @pyqtSlot()
    def on_export_to_share_file_action(self):
        logger.info('导出规则到文件进行分享')
        # 这里用完整路径可以设置默认名称
        file_info = QFileDialog.getSaveFileName(self, "选择输出目录文件",
                                                os.path.join(resource_path('.'), 'rss订阅规则分享.json'),
                                                "json 文件(*.json)")
        share_file_path = file_info[0]
        logger.info(f'导出文件 {share_file_path}')
        if not share_file_path:
            # 没有选择文件时的异常处理
            return
        with open(share_file_path, 'w', encoding='utf-8') as f:
            # 旧版数据
            # f.write(json.dumps(clean_data_list(g.data_list), ensure_ascii=False, indent=4))
            # v1 结构数据
            output_data = {
                "version": "v1",
                "data_group": {
                    'name': g.data_groups[g.current_data_list_index]['name'],
                    'data': g.clean_group_data(g.data_groups[g.current_data_list_index]['data'])
                }
            }
            f.write(json.dumps(output_data, ensure_ascii=False, indent=4))

    @pyqtSlot()
    def on_export_click(self):
        logger.info('生成qb订阅规则')

        # 尝试通过api和qb通信
        if g.config['use_qb_api'] == 1 and check_qb_port_open(g.config['qb_api_ip'], g.config['qb_api_port']):
            # 使用qb的api, 可以不重启qb
            try:
                qb_client.auth_log_in(username=g.config['qb_api_username'], password=g.config['qb_api_password'])
                # 要先加feed
                rss_feeds = qb_client.rss_items()
                rss_urls = [rss_feeds[x]['url'] for x in rss_feeds]

                for x in clean_data_list(g.data_list):
                    feed_url = x[6]
                    if feed_url not in rss_urls:
                        # 第一个参数是feed的url地址 第二个是feed的名称, 似乎通过api加会自动变成正确命名
                        qb_client.rss_add_feed(feed_url, feed_url)
                        rss_urls.append(feed_url)

                # 清空已有规则
                rss_rules = qb_client.rss_rules()
                for x in rss_rules:
                    qb_client.rss_remove_rule(x)
                # 添加新规则
                for x in clean_data_list(g.data_list):
                    qb_client.rss_set_rule(
                        rule_name=x[0] + ' ' + x[1],
                        rule_def={
                            "enabled": True,
                            "mustContain": x[2],
                            "mustNotContain": x[3],
                            "savePath": format_path_by_system(x[5]),
                            "affectedFeeds": [x[6], ],
                            "assignedCategory": x[7]
                        }
                    )
                # api通信不需要执行qb的exe
                # subprocess.Popen([g.config['qb_executable']])

                # 如果api执行成功 就可以直接返回了
                return

            # except qbittorrentapi.LoginFailed as e:
            #     logger.error(e)
            except Exception as e:
                logger.error(e)
                self.text_browser.append('通过api连接qb失败')
                self.text_browser.append(f'报错信息 {repr(e)}')

        else:
            # 不使用qb的api, 需要重启qb
            # 不使用qb的api暂时不方便添加feed
            output_data = {}
            for x in clean_data_list(g.data_list):
                logger.info(x)
                item = {
                    "enabled": True,
                    "mustContain": x[2],
                    "mustNotContain": x[3],
                    "savePath": format_path_by_system(x[5]),
                    "affectedFeeds": [x[6], ],
                    "assignedCategory": x[7]
                }

                output_data[x[0] + ' ' + x[1]] = item
            logger.info(g.config['rules_path'])
            with open(g.config['rules_path'], 'w', encoding='utf-8') as f:
                f.write(json.dumps(output_data, ensure_ascii=False))
            logger.info(g.config['open_qb_after_export'])
            if g.config['open_qb_after_export']:
                # 关闭qb
                if os.name == 'nt':
                    try:
                        qb_executable_name = format_path(g.config['qb_executable']).rsplit('/', 1)[-1]
                        os.system(f'taskkill /f /im {qb_executable_name}')
                    except:
                        pass
                # 启动qb
                subprocess.Popen([g.config['qb_executable']])
                if os.name == 'nt':
                    # windows 刷新任务栏托盘图标
                    refresh_tray()

    @pyqtSlot()
    def on_load_config_click(self):
        self.tableWidget.blockSignals(True)
        # 这里要覆盖变量
        g.config, g.data_list = g.init_config()

        # 重新渲染数据
        for cx, row in enumerate(g.data_list):
            for cy, d in enumerate(row):
                item = QTableWidgetItem(d)
                if cy in g.config['center_columns']:
                    item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(cx, cy, item)
        self.tableWidget.blockSignals(False)

    @pyqtSlot()
    def on_save_click(self):
        g.config['full_window_width'] = self.normalGeometry().width()
        g.config['full_window_height'] = self.normalGeometry().height()
        column_width_list_tmp = []
        for i in range(len(headers)):
            column_width_list_tmp.append(self.tableWidget.columnWidth(i))
        g.config['column_width_list'] = column_width_list_tmp
        save_config()
        # 不使用弹窗了，点击太麻烦
        # self.show_message("保存成功", "不错不错")
        # 提示信息
        self.text_browser.clear()
        self.text_browser.append(f'保存成功!')

    @pyqtSlot()
    def on_clean_row_click(self):
        # 防止触发 cellChange 事件导致重复更新
        self.tableWidget.blockSignals(True)
        g.data_list = clean_data_list(g.data_list)
        # 长度补充
        if len(g.data_list) < g.config['max_row_size']:
            for _ in range(g.config['max_row_size'] - len(g.data_list)):
                g.data_list.append(['' for x in range(len(headers))])
        # 更新整个列表
        for cx, row in enumerate(g.data_list):
            for cy, d in enumerate(row):
                item = QTableWidgetItem(d)
                if cy in g.config['center_columns']:
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
                        if new_c in g.config['center_columns']:
                            item.setTextAlignment(Qt.AlignCenter)

                        self.tableWidget.setItem(new_r, new_c, item)
                        g.data_list[new_r][new_c] = cell_data
                        logger.info(f'粘贴结果 {g.data_list}')
                    # 更新数据
                    g.update_data_list()
                    # 保存结果
                    if g.config['auto_save']:
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
                    if new_c in g.config['center_columns']:
                        item.setTextAlignment(Qt.AlignCenter)
                    self.tableWidget.setItem(new_r, new_c, item)
                    g.data_list[new_r][new_c] = cell.data()
                    logger.info(f'粘贴结果 {g.data_list}')
                # 更新数据
                g.update_data_list()
                # 保存结果
                if g.config['auto_save']:
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
                g.data_list[r][c] = ""
            # 更新数据
            g.update_data_list()
            if g.config['auto_save']:
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
                    g.data_list[new_r][new_c] = cell_data
                    logger.info(f'粘贴结果 {g.data_list}')
                # 更新数据
                g.update_data_list()
                # 保存结果
                if g.config['auto_save']:
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
        g.data_list[r] = ['' for _ in range(len(headers))]
        cx = r
        for cy in range(len(headers)):
            item = QTableWidgetItem('')
            if cy in g.config['center_columns']:
                item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget.setItem(cx, cy, item)
        # 更新数据
        g.update_data_list()
        # 保存结果
        if g.config['auto_save']:
            save_config()
        self.tableWidget.blockSignals(False)

    def menu_delete_all_action(self):
        # 右键菜单 删除所有订阅
        logger.info('删除所有订阅')
        self.tableWidget.blockSignals(True)
        for x in range(len(g.data_list)):
            g.data_list[x] = ['' for _ in range(len(headers))]
        for cx in range(len(g.data_list)):
            for cy in range(len(headers)):
                item = QTableWidgetItem('')
                if cy in g.config['center_columns']:
                    item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget.setItem(cx, cy, item)
        # 更新数据
        g.update_data_list()
        # 保存结果
        if g.config['auto_save']:
            save_config()
        self.tableWidget.blockSignals(False)

    def resizeEvent(self, event):
        logger.info("Window has been resized")
        g.config['full_window_width'] = self.normalGeometry().width()
        g.config['full_window_height'] = self.normalGeometry().height()
        save_config(update_data=False)

    def closeEvent(self, event):
        # 主窗口的关闭按钮事件
        if g.config['close_to_tray']:
            logger.info('关闭按钮最小化到任务栏托盘')
            self.hide()
            self.tray_icon.show()
            event.ignore()
        else:
            sys.exit()


sys.excepthook = catch_exceptions

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 加上这个表头才有样式
    app.setStyle(QStyleFactory.create('Fusion'))
    ex = App()
    sys.exit(app.exec_())
