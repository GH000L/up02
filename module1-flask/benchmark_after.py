"""
Замер производительности ПОСЛЕ оптимизации
- С кэшированием Redis
- С параллельными запросами
"""

import requests
import time
import statistics
import concurrent.futures
from datetime import datetime

def measure_time(func, name):
    times = []
    for i in range(5):
        start = time.time()
        result = func()
        end = time.time()
        elapsed = (end - start) * 1000
        times.append(elapsed)
        print(f"  Замер {i+1}: {elapsed:.2f} мс")
    
    avg = statistics.mean(times)
    print(f"\n📊 {name}: {avg:.2f} мс (среднее)")
    return avg

def get_channels_cached():
    """Получение каналов (с кэшем)"""
    response = requests.get("http://localhost:5004/channels", timeout=5)
    return response.status_code

def send_notification_parallel():
    """Параллельная отправка 5 уведомлений"""
    def send_one():
        return requests.post(
            "http://localhost:5001/notify",
            json={"channel": "email", "to": "test@mail.com", "template": "test"}
        ).status_code
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(send_one) for _ in range(5)]
        results = [f.result() for f in futures]
    return results

print("="*60)
print("ЗАМЕР ПРОИЗВОДИТЕЛЬНОСТИ (ПОСЛЕ ОПТИМИЗАЦИИ)")
print(f"Время начала: {datetime.now().strftime('%H:%M:%S')}")
print("="*60)

# Замер с кэшем
print("\n1️⃣ Получение каналов (с кэшем Redis):")
cache_time = measure_time(get_channels_cached, "GET /channels (cached)")

# Замер параллельных запросов
print("\n2️⃣ Параллельная отправка 5 уведомлений:")
start = time.time()
send_notification_parallel()
parallel_time = (time.time() - start) * 1000
print(f"  Общее время: {parallel_time:.2f} мс")
print(f"  Среднее на уведомление: {parallel_time/5:.2f} мс")

print("\n" + "="*60)
print("ИТОГОВЫЙ ОТЧЁТ ПОСЛЕ ОПТИМИЗАЦИИ:")
print(f"  GET /channels (с кэшем): {cache_time:.2f} мс")
print(f"  Параллельная отправка 5: {parallel_time:.2f} мс")
print("="*60)
