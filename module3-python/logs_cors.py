from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

statuses = {}

@app.route('/status/<notification_id>', methods=['GET'])
def get_status(notification_id):
    if notification_id not in statuses:
        return jsonify({"error": "Не найдено"}), 404
    return jsonify(statuses[notification_id])

@app.route('/log', methods=['POST'])
def log_notification():
    data = request.json
    if not data or "notification_id" not in data:
        return jsonify({"error": "Нет ID"}), 400
    
    statuses[data["notification_id"]] = {
        "notification_id": data["notification_id"],
        "channel": data.get("channel", "unknown"),
        "status": data.get("status", "unknown"),
        "sent_at": datetime.now().isoformat()
    }
    return jsonify({"status": "записано"})

@app.route('/logs', methods=['GET'])
def get_all_logs():
    return jsonify(list(statuses.values()))

if __name__ == "__main__":
    app.run(port=5003, debug=True)
