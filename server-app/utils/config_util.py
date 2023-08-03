import json


# 读取config.json文件
def read_config():
    with open('config.json', 'r') as f:
        config_data = json.load(f)
    return config_data


# 写入config.json文件
def write_config(config_data):
    with open('config.json', 'w') as f:
        json.dump(config_data, f)
