import requests
from datetime import datetime

print("="*50)
print("ТЕСТИРОВАНИЕ ЛОГИРОВАНИЯ")
print("="*50)
print()

# Успешный запрос
print("1️⃣ УСПЕШНЫЙ ЗАПРОС:")
print("Отправка уведомления...")
try:
    response = requests.post(
        "http://localhost:5001/notify",
        json={
            "channel": "email",
            "to": "test@example.com",
            "template": "welcome",
            "data": {"name": "Test User"}
        },
        timeout=3
    )
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    print("✅ ЛОГ УСПЕХА ЗАПИСАН\n")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# Ошибочный запрос (нет поля 'to')
print("2️⃣ ОШИБОЧНЫЙ ЗАПРОС (нет поля 'to'):")
print("Отправка уведомления...")
try:
    response = requests.post(
        "http://localhost:5001/notify",
        json={
            "channel": "email",
            "template": "welcome"
        },
        timeout=3
    )
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
    print("❌ ЛОГ ОШИБКИ ЗАПИСАН\n")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# Ещё один ошибочный запрос (неверный канал)
print("3️⃣ ОШИБОЧНЫЙ ЗАПРОС (неверные данные):")
print("Отправка уведомления...")
try:
    response = requests.post(
        "http://localhost:5001/notify",
        json={
            "wrong_field": "value"
        },
        timeout=3
    )
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

print()
print("="*50)
print("ЛОГИ СОХРАНЕНЫ В ФАЙЛ:")
print("  - logs/api.log (в папке module1-flask)")
print("="*50)

# Попробуем показать логи из файла
try:
    with open("../module1-flask/logs/api.log", "r") as f:
        logs = f.readlines()
        print("\n📋 ПОСЛЕДНИЕ ЛОГИ:")
        for line in logs[-5:]:
            print(f"  {line.strip()}")
except:
    print("\n⚠️ Не удалось прочитать файл логов")
