from flask import Flask, request, jsonify
from flask_cors import CORS
from loguru import logger
import uuid
import sys
from datetime import datetime

# Настройка логов
logger.remove()
logger.add(sys.stdout, format="{time:HH:mm:ss} | {level} | {message}", level="INFO")
logger.add("logs/api.log", rotation="1 day", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")

app = Flask(__name__)
CORS(app)
queue = []

@app.route('/notify', methods=['POST'])
def send_notification():
    data = request.json
    logger.info(f"Получен запрос на отправку: {data}")
    
    if not data or 'channel' not in data or 'to' not in data or 'template' not in data:
        logger.error(f"Ошибка валидации: не хватает полей в {data}")
        return jsonify({'error': 'Не хватает полей'}), 400
    
    try:
        notification_id = str(uuid.uuid4())
        task = {
            'id': notification_id,
            'channel': data['channel'],
            'to': data['to'],
            'template': data['template'],
            'data': data.get('data', {})
        }
        queue.append(task)
        logger.success(f"Уведомление создано: {notification_id} для {data['to']}")
        return jsonify({'status': 'принято', 'notification_id': notification_id}), 200
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}")
        return jsonify({'error': 'Внутренняя ошибка'}), 500

@app.route('/queue', methods=['GET'])
def get_queue():
    logger.debug(f"Запрос очереди, текущий размер: {len(queue)}")
    return jsonify({'queue': queue, 'count': len(queue)})

if __name__ == '__main__':
    logger.info("🚀 Модуль API запущен на порту 5001")
    app.run(port=5001, debug=True)

@app.route('/logs', methods=['GET'])
def get_logs():
    """Эндпоинт для просмотра логов (для мониторинга)"""
    try:
        with open('logs/api.log', 'r') as f:
            lines = f.readlines()[-50:]  # последние 50 строк
        return jsonify({'logs': lines})
    except:
        return jsonify({'logs': []})
