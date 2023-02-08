import os
import re
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

def remove_tail_slash(s):
    """去除末尾斜杠"""
    return s.rstrip('/')


def get_series_from_season_path(season_path):
    """
    修正系列名称获取 去掉结尾的年份
    来自 Episode-ReName 项目, 做了一些修改
    """
    season_path = remove_tail_slash(format_path(season_path))
    try:
        series = os.path.basename(os.path.dirname(season_path))
        pat = '\(\d{4}\)$'
        res = re.search(pat, series)
        if res:
            year = res[0][1:-1]
            series = series[:-6].strip()
        else:
            year = ''
        return series, year
    except:
        return ''

