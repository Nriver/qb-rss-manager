import g
from g import headers


def legacy_data_parser():
    """旧数据解析"""
    result = []
    return result


def fill_up_list(data_list, row_count, col_count):
    # 补到 max_row_size 个数据
    if len(data_list) < g.config['max_row_size']:
        for _ in range(g.config['max_row_size'] - len(data_list)):
            data_list.append(['' for x in range(len(headers))])
