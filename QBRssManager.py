import json
import os
import subprocess
import sys
import time

import win32gui
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QDesktopWidget, \
    QStyleFactory, QPushButton, QHBoxLayout, QMessageBox, QMenu, QAction
from win32con import WM_MOUSEMOVE

# 表头
headers = ['播出时间', '番剧名称', '包含关键字', '排除关键字', '保存路径', 'RSS订阅地址']

# 配置
config = {}


def clean_data_list():
    cleaned_data = []
    for x in data_list:
        if all(y == '' for y in x):
            continue
        cleaned_data.append(x)
    return cleaned_data


def save_config():
    # 保存配置
    with open('config.json', 'w', encoding='utf-8') as f:
        config['data_list'] = clean_data_list()
        f.write(json.dumps(config, ensure_ascii=False, indent=4))


try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.loads(f.read())
        data_list = config['data_list']
        if 'auto_save' not in config:
            config['auto_save'] = 0
        if 'max_row_size' not in config:
            config['max_row_size'] = 100
except:

    # 默认配置
    # rules_path = r'E:\soft\bt\qBittorrent\profile\qBittorrent\config\rss\download_rules.json'
    rules_path = os.path.expandvars(r'%appdata%\qBittorrent\rss\download_rules.json')
    # 保存后打开qb主程序 1为自动打开 其它值不自动打开
    open_qb_after_export = 1
    # qb主程序路径
    # qb_executable = r'E:\soft\bt\qBittorrent\qbittorrent_x64.exe'
    qb_executable = os.path.expandvars(r'%ProgramW6432%\qBittorrent\qbittorrent_x64.exe')
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

    with open('config.json', 'w', encoding='utf-8') as f:
        config['data_list'] = data_list
        f.write(json.dumps(config, ensure_ascii=False, indent=4))
    # 生成配置直接退出
    sys.exit()

# 补到 max_row_size 个数据
if len(data_list) < config['max_row_size']:
    for _ in range(config['max_row_size'] - len(data_list)):
        data_list.append(['' for x in range(len(headers))])


def format_path(s):
    return s.replace('\\', '/').replace('//', '/')


qb_executable_name = format_path(config['qb_executable']).rsplit('/', 1)[-1]


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'qbitorrent 订阅下载规则管理 by Nriver'
        # 图标
        self.setWindowIcon(QtGui.QIcon(resource_path('QBRssManager.ico')))
        self.left = 0
        self.top = 0
        self.width = 1400
        self.height = 800

        # ctrl+c
        self.copied_cells = []

        self.initUI()

    def center(self):
        # 窗口居中
        qr = self.frameGeometry()
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
        self.layout_button.addWidget(self.save_button)
        self.layout_button.addWidget(self.output_button)
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.layout_button)
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)
        # 居中显示
        self.center()
        self.show()

    def createButton(self):
        self.output_button = QPushButton('生成qb订阅规则', self)
        self.output_button.setToolTip('生成qb订阅规则')
        self.output_button.clicked.connect(self.on_export_click)

        self.move_up_button = QPushButton('上移', self)
        self.move_up_button.clicked.connect(self.on_move_up_click)
        self.move_down_button = QPushButton('下移', self)
        self.move_down_button.clicked.connect(self.on_move_down_click)

        self.save_button = QPushButton('保存配置', self)
        self.save_button.clicked.connect(self.on_save_click)

        self.clean_row_button = QPushButton('清理空行', self)
        self.clean_row_button.clicked.connect(self.on_clean_row_click)

    def createTable(self):
        self.tableWidget = QTableWidget()
        # 行数
        self.tableWidget.setRowCount(len(data_list))
        # 列数
        self.tableWidget.setColumnCount(len(headers))

        # 渲染表头
        for i, x in enumerate(headers):
            item = QTableWidgetItem(x)
            item.setForeground(QtGui.QColor(0, 0, 255))
            self.tableWidget.setHorizontalHeaderItem(i, item)

        # 渲染数据
        # 空数据处理
        if not data_list:
            for x in range(len(headers)):
                self.tableWidget.setItem(0, x, QTableWidgetItem(""))
        else:
            for cx, row in enumerate(data_list):
                for cy, d in enumerate(row):
                    self.tableWidget.setItem(cx, cy, QTableWidgetItem(d))

        self.tableWidget.move(0, 0)

        # 宽度自适应 效果不太好
        # self.tableWidget.resizeColumnsToContents()
        # 拉长
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        # header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        # header.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)

        # self.tableWidget.setColumnWidth(0, 100)
        self.tableWidget.setColumnWidth(1, 260)
        self.tableWidget.setColumnWidth(2, 210)
        # self.tableWidget.setColumnWidth(3, 100)
        # self.tableWidget.setColumnWidth(4, 400)
        self.tableWidget.setColumnWidth(5, 300)

        # 双击事件绑定
        self.tableWidget.doubleClicked.connect(self.on_double_click)

        # 修改事件绑定
        self.tableWidget.cellChanged.connect(self.on_cell_changed)

        self.tableWidget.keyPressEvent = self.handle_key_press

        # 右键菜单
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.generateMenu)

    def generateMenu(self, pos):
        # 右键弹窗菜单
        # 右键弹窗菜单加一个sleep, 防止长按右键导致右键事件被重复触发
        time.sleep(0)
        print("pos======", pos)
        self.menu = QMenu(self)
        self.delete_action = QAction("删除")
        self.delete_action.triggered.connect(self.menu_delete_action)
        self.menu.addAction(self.delete_action)
        self.menu.exec_(self.tableWidget.mapToGlobal(pos))
        return

    @pyqtSlot()
    def on_double_click(self):
        # 双击事件
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())

    @pyqtSlot()
    def on_move_up_click(self):
        print('on_move_up_click()')
        # 上移事件
        # 防止触发 cellChange 事件导致重复更新
        self.tableWidget.blockSignals(True)
        r = self.tableWidget.currentRow()
        c = self.tableWidget.currentColumn()
        if r == 0:
            return

        data_list[r], data_list[r - 1] = data_list[r - 1], data_list[r]

        for i in range(len(headers)):
            self.tableWidget.setItem(r, i, QTableWidgetItem(data_list[r][i]))
            self.tableWidget.setItem(r - 1, i, QTableWidgetItem(data_list[r - 1][i]))

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
        if r == len(data_list):
            return

        data_list[r], data_list[r + 1] = data_list[r + 1], data_list[r]

        for i in range(len(headers)):
            self.tableWidget.setItem(r, i, QTableWidgetItem(data_list[r][i]))
            self.tableWidget.setItem(r + 1, i, QTableWidgetItem(data_list[r + 1][i]))

        self.tableWidget.setCurrentCell(r + 1, c)
        if config['auto_save']:
            save_config()
        self.tableWidget.blockSignals(False)

    @pyqtSlot()
    def on_cell_changed(self):
        print('on_cell_changed()')
        # 修改事件
        r = self.tableWidget.currentRow()
        c = self.tableWidget.currentColumn()
        text = self.tableWidget.currentItem().text()
        print(r, c, text)
        # 修改数据
        data_list[r][c] = text
        print('on_cell_changed 结果', data_list)
        if config['auto_save']:
            save_config()

    @pyqtSlot()
    def on_export_click(self):
        print('生成qb订阅规则')
        output_data = {}
        for x in clean_data_list():
            print(x)
            item = {
                "enabled": True,
                "mustContain": x[2],
                "mustNotContain": x[3],
                "savePath": format_path(x[4]),
                "affectedFeeds": [x[5], ]
            }

            output_data[x[1] + '  ' + x[2]] = item
        print(config['rules_path'])
        with open(config['rules_path'], 'w', encoding='utf-8') as f:
            f.write(json.dumps(output_data, ensure_ascii=False))
        print(config['open_qb_after_export'])
        if config['open_qb_after_export']:
            # 关闭qb
            try:
                os.system(f'taskkill /f /im {qb_executable_name}')
            except:
                pass
            # 启动qb
            subprocess.Popen([config['qb_executable']])
            # 刷新任务栏图标
            refresh_tray()

    @pyqtSlot()
    def on_save_click(self):
        save_config()
        self.msg = QMessageBox()
        # Set the information icon
        self.msg.setIcon(QMessageBox.Information)
        # Set the main message
        self.msg.setText("保存成功")
        # Set the title of the window
        self.msg.setWindowTitle("不错不错")
        # Display the message box
        self.msg.show()

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
                self.tableWidget.setItem(cx, cy, QTableWidgetItem(d))

        self.tableWidget.blockSignals(False)

    def handle_key_press(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_F2):
            print('edit cell')
            self.tableWidget.edit(self.tableWidget.currentIndex())

        #   复制粘贴
        elif event.key() == Qt.Key_C and (event.modifiers() & Qt.ControlModifier):
            print('ctrl c')
            self.copied_cells = sorted(self.tableWidget.selectedIndexes())
            print(f'复制了 {len(self.copied_cells)} 个')
        elif event.key() == Qt.Key_V and (event.modifiers() & Qt.ControlModifier):
            print('ctrl v')
            self.tableWidget.blockSignals(True)
            if not self.copied_cells:
                return
            r = self.tableWidget.currentRow() - self.copied_cells[0].row()
            c = self.tableWidget.currentColumn() - self.copied_cells[0].column()
            print(f'准备粘贴 {len(self.copied_cells)} 个')
            for cell in self.copied_cells:
                new_r = cell.row() + r
                new_c = cell.column() + c
                if new_c > (len(headers) - 1):
                    # 忽略跨行数据 防止数组越界
                    continue
                print('粘贴数据', new_r, new_c, cell.data())
                self.tableWidget.setItem(new_r, new_c, QTableWidgetItem(cell.data()))
                data_list[new_r][new_c] = cell.data()
                print('粘贴结果', data_list)
            # 保存结果
            if config['auto_save']:
                save_config()
            self.tableWidget.blockSignals(False)

        # 删除数据
        elif event.key() == Qt.Key_Delete:
            print('delete')
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
            print('Move right')
            self.tableWidget.setCurrentCell(self.tableWidget.currentRow(),
                                            min(self.tableWidget.currentColumn() + 1, len(headers) - 1))
        elif event.key() == Qt.Key_Left:
            print('Move left')
            self.tableWidget.setCurrentCell(self.tableWidget.currentRow(),
                                            max(self.tableWidget.currentColumn() - 1, 0))
        elif event.key() == Qt.Key_Up:
            print('Move up')
            self.tableWidget.setCurrentCell(max(self.tableWidget.currentRow() - 1, 0),
                                            self.tableWidget.currentColumn())
        elif event.key() == Qt.Key_Down:
            print('Move down')
            self.tableWidget.setCurrentCell(max(self.tableWidget.currentRow() + 1, 0),
                                            self.tableWidget.currentColumn())

        elif event.key() == Qt.Key_I and (event.modifiers() & Qt.ControlModifier):
            # 导入excel数据
            print('ctrl i')
            self.tableWidget.blockSignals(True)
            r = self.tableWidget.currentRow()
            c = self.tableWidget.currentColumn()
            rows = app.clipboard().text().split('\n')
            for b_r, row in enumerate(rows):
                if not row:
                    continue
                cells = row.split('\t')
                print(cells)

                for b_c, cell_data in enumerate(cells):
                    new_r = b_r + r
                    new_c = b_c + c
                    if new_c > (len(headers) - 1):
                        # 忽略跨行数据 防止数组越界
                        continue
                    print('粘贴数据', new_r, new_c, cell_data)
                    self.tableWidget.setItem(new_r, new_c, QTableWidgetItem(cell_data))
                    data_list[new_r][new_c] = cell_data
                    print('粘贴结果', data_list)
                # 保存结果
                if config['auto_save']:
                    save_config()
            self.tableWidget.blockSignals(False)

        # return

    def menu_delete_action(self):
        # 右键菜单 删除
        r = self.tableWidget.currentRow()
        print(r)
        self.tableWidget.blockSignals(True)
        data_list.pop(r)
        self.on_clean_row_click()
        self.tableWidget.blockSignals(False)


def refresh_tray():
    # 刷新任务栏图标, 去掉强制关闭进程后的残留图标
    hShellTrayWnd = win32gui.FindWindow("Shell_trayWnd", "")
    hTrayNotifyWnd = win32gui.FindWindowEx(hShellTrayWnd, 0, "TrayNotifyWnd", None)
    hSysPager = win32gui.FindWindowEx(hTrayNotifyWnd, 0, 'SysPager', None)
    if hSysPager:
        hToolbarWindow32 = win32gui.FindWindowEx(hSysPager, 0, 'ToolbarWindow32', None)
    else:
        hToolbarWindow32 = win32gui.FindWindowEx(hTrayNotifyWnd, 0, 'ToolbarWindow32', None);
    print('hToolbarWindow32', hToolbarWindow32)
    if hToolbarWindow32:
        rect = win32gui.GetWindowRect(hToolbarWindow32)
        print(rect)
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
