# 配置
import json
import os
import sys

from loguru import logger

headers = ['播出时间', '剧集名称', '包含关键字', '排除关键字', '集数修正', '保存路径', 'RSS订阅地址', '种子类型']

# 配置
config = {}
# 屏幕上显示的数据
data_list = []
# 所有的分组数据
data_groups = []
# 记录目前的data_list是第几组数据
current_data_list_index = 0

new_data_group = {
    'name': '新分组',
    'keyword_override': '',
    'rss_override': '',
    'data': [],
}


def get_default_config():
    # 默认配置

    default_data_dump = {
        'version': 'v1',
        'data_groups': [
            {
                'name': '默认分组',
                'keyword_override': '',
                'rss_override': '',
                'data': [],
            }
        ]
    }

    if os.name == 'nt':
        # Windows 系统默认配置
        # qb主程序路径
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

    default_config = {
        # 自动保存
        'auto_save': 0,
        'column_width_list': [80, 260, 210, 65, 62, 370, 290, 80],
        'center_columns': [0, 3, 4],
        'close_to_tray': 1,
        'data_dump': default_data_dump,
        'date_auto_zfill': 1,
        'full_window_width': 1400,
        'full_window_height': 800,
        'max_row_size': 100,
        # 保存后打开qb主程序 1为自动打开 其它值不自动打开
        'open_qb_after_export': 1,
        # qb 本机操作
        'qb_executable': qb_executable,
        'feeds_json_path': feeds_json_path,
        'rss_article_folder': rss_article_folder,
        'rules_path': rules_path,
        # qb api通信相关
        'use_qb_api': 1,
        'qb_api_ip': '127.0.0.1',
        'qb_api_port': 8080,
        'qb_api_username': 'admin',
        'qb_api_password': 'adminadmin',
        'keyword_default': '{series_name}',
        'rss_default': '',
    }

    return default_config


def init_config():
    global config
    global data_list
    global data_groups
    global current_data_list_index

    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.loads(f.read())
            # 修正配置，补充缺少的默认配置
            default_config = get_default_config()
            for x in default_config:
                if x not in config:
                    config[x] = default_config[x]

        if 'data_list' in config:
            parse_legacy()
        elif 'data_dump' in config and config['data_dump']['version'] == 'v1':
            # 从config里加载data groups数据，后面的操作不要直接操作config对象，直接操作data_groups
            data_groups = config['data_dump']['data_groups']
            # 修正配置，补充缺少的默认配置
            for i in range(len(data_groups)):
                for y in new_data_group:
                    if y not in data_groups[i]:
                        data_groups[i][y] = new_data_group[y]

            parse_v1()
        else:
            exit()
    except:
        # 配置解析错误
        if not os.path.exists('config.json'):
            # 不存在配置文件 生成默认配置

            default_config = get_default_config()
            config = default_config

            with open('config.json', 'w', encoding='utf-8') as f:
                f.write(json.dumps(config, ensure_ascii=False, indent=4))
        else:
            logger.error('配置解析报错!')
        # 直接退出
        sys.exit()

    return config, data_list


def clean_data_list(tmp_data_list):
    """清理空行"""
    cleaned_data = []
    for x in tmp_data_list:
        if all(y == '' for y in x):
            continue
        cleaned_data.append(x)
    return cleaned_data


def clean_group_data(tmp_group_data):
    """清理v1结构空行"""
    cleaned_data = []
    for x in tmp_group_data:
        if all(x[y] == '' for y in x):
            continue
        cleaned_data.append(x)
    return cleaned_data


def save_config(update_data=True):
    """保存配置"""
    global config
    global data_list
    global data_groups
    global current_data_list_index

    logger.info(f'保存配置 更新数据 {update_data}')

    # 读取原始数据，以防异常报错丢失配置
    with open('config.json', 'r', encoding='utf-8') as f:
        original_content = f.read()

    with open('config.json', 'w', encoding='utf-8') as f:
        try:
            if update_data:
                config['data_dump'] = dump_v1()
            f.write(json.dumps(config, ensure_ascii=False, indent=4))
        except:
            logger.info('数据解析有问题! 还原数据!')
            f.write(original_content)
            return '数据解析有问题! 还原数据!'


def parse_v1():
    global config
    global data_list
    global data_groups
    global current_data_list_index

    data_list = []
    for x in data_groups[current_data_list_index]['data']:
        data_list.append(convert_v1_line(x))

    # 补到 max_row_size 个数据
    fill_up_data_list()

    return config, data_list


def parse_v1_line(x):
    parsed_line = {
        'release_date': x[0],
        'series_name': x[1],
        'mustContain': x[2],
        'mustNotContain': x[3],
        'rename_offset': x[4],
        'savePath': x[5],
        'affectedFeeds': x[6],
        'assignedCategory': x[7],
    }
    return parsed_line


def parse_v1_data_list(tmp_data_list):
    data = []
    for x in tmp_data_list:
        line = parse_v1_line(x)
        data.append(line)
    return data


def convert_v1_line(x):
    converted_list = [
        x['release_date'],
        x['series_name'],
        x['mustContain'],
        x['mustNotContain'],
        x['rename_offset'],
        x['savePath'],
        x['affectedFeeds'],
        x['assignedCategory'],
    ]
    return converted_list


def dump_v1():
    global data_groups

    data_dump = {
        'version': 'v1',
        'data_groups': [],
    }

    for data_group in data_groups:
        cleaned_group_data = clean_group_data(data_group['data'])
        data_dump['data_groups'].append({
            'name': data_group['name'],
            'keyword_override': data_group['keyword_override'],
            'rss_override': data_group['rss_override'],
            'data': cleaned_group_data,
        })

    return data_dump


def update_data_list(text=None, r=None, c=None):
    """更新data_groups里的data_list数据到最新"""
    global config
    global data_list
    global data_groups
    global current_data_list_index

    if text and r and c:
        data_list[r][c] = text
    data_groups[current_data_list_index]['data'] = parse_v1_data_list(data_list)


def fill_up_data_list():
    global data_list
    # 补到 max_row_size 个数据
    if len(data_list) < config['max_row_size']:
        for _ in range(config['max_row_size'] - len(data_list)):
            data_list.append(['' for x in range(len(headers))])


def parse_legacy():
    """处理旧版数据格式"""
    global config
    global data_list
    global data_groups
    global current_data_list_index

    data_list = config['data_list']

    # 补到 max_row_size 个数据
    fill_up_data_list()

    data_groups = [
        {
            'name': '默认分组',
            'keyword_override': '',
            'rss_override': '',
            'data': [],
        }
    ]

    data = parse_v1_data_list(data_list)
    current_data_list_index = 0
    data_groups[current_data_list_index]['data'] = data

    # 去除旧版数据
    del config['data_list']

    # 保存新版数据
    config['data_dump'] = dump_v1()

    return


def data_dump_to_list(data_dump):
    pass


def data_list_to_dump(data_list):
    logger.info('data_list_to_dump()')
