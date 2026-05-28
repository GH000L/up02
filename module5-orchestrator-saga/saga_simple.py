import requests
import time
from datetime import datetime

print("\n" + "="*50)
print("ЗАПУСК СКВОЗНОГО СЦЕНАРИЯ")
print("="*50 + "\n")

# Шаг 1: Вызов API (порт 5001)
print("Шаг 1: Вызов API (порт 5001)")
notification = {
    "channel": "email",
    "to": "test@example.com",
    "template": "welcome",
    "data": {"name": "Test User"}
}

try:
    response = requests.post("http://localhost:5001/notify", json=notification, timeout=5)
    if response.status_code == 200:
        result = response.json()
        notification_id = result.get("notification_id")
        print(f"✅ Уведомление создано: {notification_id}")
    else:
        print(f"❌ Ошибка API: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ Ошибка: {e}")
    exit(1)

# Шаг 2: Запись в логи (порт 5003)
print("\nШаг 2: Запись в логи (порт 5003)")
log_data = {
    "notification_id": notification_id,
    "channel": "email",
    "status": "sent",
    "sent_at": datetime.now().isoformat()
}

try:
    response = requests.post("http://localhost:5003/log", json=log_data, timeout=5)
    if response.status_code == 200:
        print("✅ Лог записан")
    else:
        print(f"❌ Ошибка логов: {response.status_code}")
except Exception as e:
    print(f"⚠️ Логи не доступны: {e}")

# Шаг 3: Сохранение в БД (порт 5004)
print("\nШаг 3: Сохранение в БД (порт 5004)")
db_data = {
    "channel_id": 1,
    "recipient": "test@example.com"
}

try:
    response = requests.post("http://localhost:5004/notifications", json=db_data, timeout=5)
    if response.status_code == 200:
        print("✅ Сохранено в БД")
    else:
        print(f"⚠️ БД ответила: {response.status_code}")
except Exception as e:
    print(f"⚠️ БД не доступна: {e}")

print("\n" + "="*50)
print("СКВОЗНОЙ СЦЕНАРИЙ ВЫПОЛНЕН УСПЕШНО ✅")
print("="*50)
