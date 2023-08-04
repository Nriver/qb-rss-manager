from flask import Blueprint, jsonify, request
from utils.config_util import read_config, write_config

config_bp = Blueprint('config', __name__)


@config_bp.route('/config', methods=['GET'])
def get_config():
    config_data = read_config()
    return jsonify(config_data)


@config_bp.route('/config', methods=['POST'])
def update_config_file():
    new_config_data = request.json
    write_config(new_config_data)
    return jsonify(new_config_data)


@config_bp.route("/update_config", methods=["POST"])
def update_config():
    try:
        config_data = read_config()
        new_config = request.get_json()
        # Update the config data with the new values
        config_data["use_qb_api"] = new_config.get("use_qb_api", 0)
        config_data["qb_api_ip"] = new_config.get("qb_api_ip", "127.0.0.1")
        config_data["qb_api_password"] = new_config.get("qb_api_password", "")
        config_data["qb_api_port"] = new_config.get("qb_api_port", 8080)
        config_data["qb_api_username"] = new_config.get("qb_api_username", "")
        config_data["qb_executable"] = new_config.get("qb_executable", "qbittorrent")
        config_data["feeds_json_path"] = new_config.get("feeds_json_path", "")
        config_data["rss_article_folder"] = new_config.get("rss_article_folder", "")
        config_data["rules_path"] = new_config.get("rules_path", "")
        # Call write_config function to save the updated configuration
        write_config(config_data)
        return jsonify({"message": "Config updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@config_bp.route('/save_data', methods=['POST'])
def save_data():
    try:
        config_data = read_config()
        data = request.get_json()
        config_data["data_dump"]["data_groups"] = data["data_dump"]["data_groups"]
        print(data["data_dump"]["data_groups"])
        write_config(config_data)
        return jsonify({"message": "Data saved successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Failed to save data", "details": str(e)}), 500
