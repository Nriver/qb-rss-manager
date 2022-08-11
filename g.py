# 配置
import json
import os
import sys

from loguru import logger

headers = ['播出时间', '剧集名称', '包含关键字', '排除关键字', '集数修正', '保存路径', 'RSS订阅地址', '种子类型']

config = {}
data_list = []


def init_config():
    global config
    global data_list
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
            if 'qb_api_username' not in config:
                config['qb_api_username'] = ''
            if 'qb_api_password' not in config:
                config['qb_api_password'] = ''
            if 'text_browser_height' in config:
                del config['text_browser_height']
    except:

        # 默认配置
        # rules_path = r'E:\soft\bt\qBittorrent\profile\qBittorrent\config\rss\download_rules.json'
        if os.name == 'nt':
            # Windows 系统默认配置
            # qb主程序路径
            # qb_executable = r'E:\soft\bt\qBittorrent\qbittorrent_x64.exe'
            qb_executable = os.path.expandvars(r'%ProgramW6432%\qBittorrent\qbittorrent.exe')
            # qb配置文件路径
            rules_path = os.path.expandvars(r'%appdata%\qBittorrent\rss\download_rules.json')
            feeds_json_path = os.path.expandvars(r'%appdata%\qBittorrent\rss\feeds.json')
            rss_article_folder = os.path.expandvars(r'%LOCALAPPDATA%\qBittorrent\rss\articles')
        else:
            # Linux 桌面系统默认配置
            qb_executable = os.path.expanduser(r'qbittorrent')
            rules_path = os.path.expanduser(r'~/.config/qBittorrent/rss/download_rules.json')
            feeds_json_path = os.path.expanduser(r'~/.config/qBittorrent/rss/feeds.json')
            rss_article_folder = os.path.expanduser(r'~/.config/qBittorrent/rss/articles')

        # 保存后打开qb主程序 1为自动打开 其它值不自动打开
        open_qb_after_export = 1

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

    return config, data_list


def clean_data_list(tmp_data_list):
    """清理空行"""
    cleaned_data = []
    for x in tmp_data_list:
        if all(y == '' for y in x):
            continue
        cleaned_data.append(x)
    return cleaned_data


def save_config(config, data_list, update_data=True):
    """保存配置"""
    logger.info(f'保存配置 更新数据 {update_data}')
    with open('config.json', 'w', encoding='utf-8') as f:
        if update_data:
            config['data_list'] = clean_data_list(data_list)
        f.write(json.dumps(config, ensure_ascii=False, indent=4))
