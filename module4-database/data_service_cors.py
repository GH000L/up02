from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

Base = declarative_base()

class Channel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    channel_id = Column(Integer, ForeignKey('channels.id'))
    recipient = Column(String(200), nullable=False)
    status = Column(String(50), default='pending')
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

DATABASE_URL = "postgresql://postgres:mysecretpassword@localhost:5432/notification_hub"
engine = create_engine(DATABASE_URL, echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

@app.route('/channels', methods=['GET'])
def get_channels():
    session = Session()
    channels = session.query(Channel).all()
    session.close()
    return jsonify([{'id': c.id, 'name': c.name, 'is_active': c.is_active} for c in channels])

@app.route('/notifications', methods=['POST'])
def create_notification():
    data = request.json
    session = Session()
    notification = Notification(
        channel_id=data['channel_id'],
        recipient=data['recipient'],
        status='pending'
    )
    session.add(notification)
    session.commit()
    session.close()
    return jsonify({'status': 'created', 'id': notification.id})

if __name__ == '__main__':
    session = Session()
    if session.query(Channel).count() == 0:
        channels = ['email', 'sms', 'telegram', 'push']
        for ch in channels:
            session.add(Channel(name=ch, is_active=True))
        session.commit()
        print("✅ Начальные каналы добавлены")
    session.close()
    
    print("🚀 Модуль БД запущен на порту 5004")
    app.run(port=5004, debug=True)
