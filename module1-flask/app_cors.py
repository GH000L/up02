from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)
queue = []

@app.route('/notify', methods=['POST'])
def send_notification():
    data = request.json
    if not data or 'channel' not in data or 'to' not in data or 'template' not in data:
        return jsonify({'error': 'Не хватает полей'}), 400
    
    notification_id = str(uuid.uuid4())
    task = {
        'id': notification_id,
        'channel': data['channel'],
        'to': data['to'],
        'template': data['template'],
        'data': data.get('data', {})
    }
    queue.append(task)
    
    return jsonify({'status': 'принято', 'notification_id': notification_id}), 200

@app.route('/queue', methods=['GET'])
def get_queue():
    return jsonify({'queue': queue, 'count': len(queue)})

if __name__ == '__main__':
    app.run(port=5001, debug=True)
