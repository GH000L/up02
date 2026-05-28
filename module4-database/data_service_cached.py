"""
Модуль БД с кэшированием (Redis)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
import redis
import json
import time

app = Flask(__name__)
CORS(app)

# Подключение к Redis
try:
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    redis_client.ping()
    redis_available = True
    print("✅ Redis подключён")
except:
    redis_available = False
    print("⚠️ Redis не доступен, работаем без кэша")

Base = declarative_base()

class Channel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

DATABASE_URL = "postgresql://postgres:mysecretpassword@localhost:5432/notification_hub"
engine = create_engine(DATABASE_URL, echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Кэширование с TTL 60 секунд
CACHE_TTL = 60

@app.route('/channels', methods=['GET'])
def get_channels_cached():
    """Получение каналов с кэшированием"""
    start_time = time.time()
    
    # Пытаемся получить из кэша
    if redis_available:
        cached = redis_client.get('channels_list')
        if cached:
            channels = json.loads(cached)
            elapsed = (time.time() - start_time) * 1000
            print(f"✅ КЭШ: каналы получены за {elapsed:.2f} мс")
            return jsonify(channels)
    
    # Кэша нет — идём в БД
    session = Session()
    channels = session.query(Channel).all()
    session.close()
    
    result = [{'id': c.id, 'name': c.name, 'is_active': c.is_active} for c in channels]
    
    # Сохраняем в кэш
    if redis_available:
        redis_client.setex('channels_list', CACHE_TTL, json.dumps(result))
        elapsed = (time.time() - start_time) * 1000
        print(f"📀 БД: каналы загружены за {elapsed:.2f} мс (сохранено в кэш)")
    
    return jsonify(result)

@app.route('/channels/clear-cache', methods=['POST'])
def clear_cache():
    """Очистка кэша (для администрирования)"""
    if redis_available:
        redis_client.delete('channels_list')
        return jsonify({'status': 'cache cleared'})
    return jsonify({'status': 'redis not available'})

@app.route('/notifications', methods=['POST'])
def create_notification():
    data = request.json
    session = Session()
    notification_id = str(uuid.uuid4())
    # ... остальной код
    session.close()
    
    # Инвалидируем кэш при изменении данных
    if redis_available:
        redis_client.delete('channels_list')
    
    return jsonify({'status': 'created', 'id': notification_id})

if __name__ == '__main__':
    # Заполняем начальные данные
    session = Session()
    if session.query(Channel).count() == 0:
        channels = ['email', 'sms', 'telegram', 'push']
        for ch in channels:
            session.add(Channel(name=ch, is_active=True))
        session.commit()
        print("✅ Начальные каналы добавлены")
    session.close()
    
    print("🚀 Модуль БД с кэшированием запущен на порту 5004")
    app.run(port=5004, debug=True)
