from flask import Blueprint, jsonify, request
from utils.config_util import read_config, write_config

config_bp = Blueprint('config', __name__)


@config_bp.route('/api/config', methods=['GET'])
def get_config():
    config_data = read_config()
    return jsonify(config_data)


@config_bp.route('/api/config', methods=['POST'])
def update_config():
    new_config_data = request.json
    write_config(new_config_data)
    return jsonify(new_config_data)
