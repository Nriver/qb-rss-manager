from flask import Flask, jsonify, request
from flask_cors import CORS
from utils.config_util import read_config, write_config

app = Flask(__name__)
# 允许所有来源的跨域请求
CORS(app)

# 假设有一个简单的数据列表
data_list = [{'id': 1, 'name': 'Item 1'}, {'id': 2, 'name': 'Item 2'}]


@app.route('/api/items', methods=['GET'])
def get_items():
    return jsonify(data_list)


@app.route('/api/items', methods=['POST'])
def add_item():
    new_item = request.json
    data_list.append(new_item)
    return jsonify(new_item)


@app.route('/api/config', methods=['GET'])
def get_config():
    config_data = read_config()
    return jsonify(config_data)


@app.route('/api/config', methods=['POST'])
def update_config():
    new_config_data = request.json
    write_config(new_config_data)
    return jsonify(new_config_data)


if __name__ == '__main__':
    app.run()
