"""
Замер производительности до оптимизации
"""

import requests
import time
import statistics
from datetime import datetime

def measure_time(func, name):
    """Замер времени выполнения функции"""
    times = []
    for i in range(5):  # 5 замеров
        start = time.time()
        result = func()
        end = time.time()
        elapsed = (end - start) * 1000  # в миллисекундах
        times.append(elapsed)
        print(f"  Замер {i+1}: {elapsed:.2f} мс")
    
    avg = statistics.mean(times)
    min_t = min(times)
    max_t = max(times)
    print(f"\n📊 {name}:")
    print(f"  Среднее: {avg:.2f} мс")
    print(f"  Мин: {min_t:.2f} мс")
    print(f"  Макс: {max_t:.2f} мс")
    print(f"  Медиана: {statistics.median(times):.2f} мс")
    return avg

def send_notification():
    """Отправка одного уведомления"""
    response = requests.post(
        "http://localhost:5001/notify",
        json={
            "channel": "email",
            "to": "benchmark@test.com",
            "template": "benchmark"
        },
        timeout=5
    )
    return response.status_code

def check_queue():
    """Проверка очереди"""
    response = requests.get("http://localhost:5001/queue", timeout=5)
    return response.status_code

def process_worker():
    """Обработка задачи воркером"""
    response = requests.get("http://localhost:5002/process", timeout=5)
    return response.status_code

print("="*60)
print("ЗАМЕР ПРОИЗВОДИТЕЛЬНОСТИ (ДО ОПТИМИЗАЦИИ)")
print(f"Время начала: {datetime.now().strftime('%H:%M:%S')}")
print("="*60)

# Замеры
print("\n1️⃣ Отправка уведомления (POST /notify):")
send_time = measure_time(send_notification, "POST /notify")

print("\n2️⃣ Проверка очереди (GET /queue):")
queue_time = measure_time(check_queue, "GET /queue")

print("\n3️⃣ Обработка воркером (GET /process):")
worker_time = measure_time(process_worker, "GET /process")

# Полное время сценария
print("\n" + "="*60)
print("ИТОГОВЫЙ ОТЧЁТ:")
print(f"  Отправка: {send_time:.2f} мс")
print(f"  Проверка очереди: {queue_time:.2f} мс")
print(f"  Обработка: {worker_time:.2f} мс")
print(f"  Общее время: {send_time + queue_time + worker_time:.2f} мс")
print("="*60)
