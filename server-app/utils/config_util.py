import json


# 读取config.json文件
def read_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    return config_data


# 写入config.json文件
def write_config(config_data):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)
