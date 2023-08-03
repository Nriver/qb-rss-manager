from flask import Flask, jsonify, request
from flask_cors import CORS

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


if __name__ == '__main__':
    app.run()
