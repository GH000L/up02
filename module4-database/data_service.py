from flask import Flask, request, jsonify
from models import get_session, Channel, Template, Notification
from datetime import datetime

app = Flask(__name__)

# === Каналы ===
@app.route('/channels', methods=['GET'])
def get_channels():
    session = get_session()
    channels = session.query(Channel).all()
    session.close()
    return jsonify([{'id': c.id, 'name': c.name, 'is_active': c.is_active} for c in channels])

# === Шаблоны ===
@app.route('/templates', methods=['GET'])
def get_templates():
    session = get_session()
    templates = session.query(Template).all()
    session.close()
    return jsonify([{'id': t.id, 'name': t.name, 'subject': t.subject, 'body': t.body} for t in templates])

@app.route('/templates', methods=['POST'])
def create_template():
    data = request.json
    session = get_session()
    template = Template(
        name=data['name'],
        subject=data.get('subject', ''),
        body=data['body'],
        channel_id=data['channel_id']
    )
    session.add(template)
    session.commit()
    session.close()
    return jsonify({'status': 'created', 'id': template.id})

# === Уведомления ===
@app.route('/notifications', methods=['GET'])
def get_notifications():
    session = get_session()
    notifications = session.query(Notification).order_by(Notification.created_at.desc()).limit(100).all()
    session.close()
    return jsonify([{
        'id': n.id,
        'recipient': n.recipient,
        'status': n.status,
        'sent_at': n.sent_at.isoformat() if n.sent_at else None,
        'error': n.error,
        'created_at': n.created_at.isoformat() if n.created_at else None
    } for n in notifications])

@app.route('/notifications', methods=['POST'])
def create_notification():
    data = request.json
    session = get_session()
    notification = Notification(
        channel_id=data['channel_id'],
        template_id=data.get('template_id'),
        recipient=data['recipient'],
        status='pending'
    )
    session.add(notification)
    session.commit()
    session.close()
    return jsonify({'status': 'created', 'id': notification.id})

# === Вебхук для синхронизации ===
@app.route('/webhook/sync', methods=['POST'])
def webhook_sync():
    data = request.json
    event_type = data.get('event')
    
    if event_type == 'notification_created':
        session = get_session()
        # Ищем канал по имени
        channel = session.query(Channel).filter_by(name=data.get('channel', 'email')).first()
        notification = Notification(
            channel_id=channel.id if channel else None,
            recipient=data['recipient'],
            status='pending'
        )
        session.add(notification)
        session.commit()
        notification_id = notification.id
        session.close()
        print(f"✅ Уведомление создано через вебхук: {notification_id}")
        
    elif event_type == 'notification_status_update':
        session = get_session()
        notification = session.query(Notification).filter_by(id=data['notification_id']).first()
        if notification:
            notification.status = data['status']
            if data['status'] == 'sent':
                notification.sent_at = datetime.now()
            notification.error = data.get('error', '')
            session.commit()
            print(f"✅ Статус обновлён: {data['notification_id']} -> {data['status']}")
        session.close()
    
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    from models import create_tables, get_session
    
    # Создаём таблицы
    create_tables()
    
    # Добавляем начальные каналы
    session = get_session()
    if session.query(Channel).count() == 0:
        channels = ['email', 'sms', 'telegram', 'push']
        for ch in channels:
            session.add(Channel(name=ch, is_active=True))
        session.commit()
        print("✅ Начальные каналы добавлены: email, sms, telegram, push")
    session.close()
    
    print("\n🚀 Модуль БД запущен на порту 5004")
    app.run(port=5004, debug=True)
