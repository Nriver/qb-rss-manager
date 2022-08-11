import os
import sys


def resource_path(relative_path):
    # 兼容pyinstaller的文件资源访问
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


def format_path(s):
    return s.replace('\\', '/').replace('//', '/')


def format_path_by_system(s):
    # 保存路径格式化 兼容linux路径
    # 由于有远程调用api的需求, 所以这里不能限制斜杠格式
    # 简单判断一下吧
    if not s:
        return ''
    if s[0] != '/':
        return format_path(s).replace('/', '\\')
    else:
        return format_path(s)
