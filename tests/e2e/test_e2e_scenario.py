"""
E2E тесты для Notification Hub
Аналог Playwright на Python с использованием requests
"""

import unittest
import requests
import time
from datetime import datetime

class NotificationHubE2ETest(unittest.TestCase):
    """Сквозное тестирование полного сценария"""
    
    @classmethod
    def setUpClass(cls):
        cls.api_url = "http://localhost:5001"
        cls.worker_url = "http://localhost:5002"
        cls.logs_url = "http://localhost:5003"
        cls.db_url = "http://localhost:5004"
    
    def test_e2e_email_notification(self):
        """E2E тест: отправка Email уведомления"""
        print("\n🔍 E2E Тест: Отправка Email уведомления")
        
        # Шаг 1: Отправка через UI (эмуляция)
        notification = {
            "channel": "email",
            "to": "user@example.com",
            "template": "welcome",
            "data": {"name": "Test User"}
        }
        
        response = requests.post(f"{self.api_url}/notify", json=notification, timeout=5)
        self.assertEqual(response.status_code, 200)
        notification_id = response.json().get("notification_id")
        print(f"  ✅ Уведомление создано: {notification_id}")
        
        # Шаг 2: Проверка очереди
        queue_response = requests.get(f"{self.api_url}/queue", timeout=5)
        self.assertEqual(queue_response.status_code, 200)
        print(f"  ✅ Очередь проверена")
        
        # Шаг 3: Обработка worker'ом
        process_response = requests.get(f"{self.worker_url}/process", timeout=5)
        self.assertEqual(process_response.status_code, 200)
        print(f"  ✅ Worker обработал")
        
        # Шаг 4: Запись в логи
        log_entry = {
            "notification_id": notification_id,
            "channel": "email",
            "status": "sent",
            "sent_at": datetime.now().isoformat()
        }
        log_response = requests.post(f"{self.logs_url}/log", json=log_entry, timeout=5)
        self.assertEqual(log_response.status_code, 200)
        print(f"  ✅ Лог записан")
        
        # Шаг 5: Проверка логов
        logs_response = requests.get(f"{self.logs_url}/logs", timeout=5)
        self.assertEqual(logs_response.status_code, 200)
        logs = logs_response.json()
        
        found = any(log.get("notification_id") == notification_id for log in logs)
        self.assertTrue(found, "Уведомление не найдено в логах")
        print(f"  ✅ Лог подтверждён")
        
        print(f"  🎉 E2E тест пройден!")
    
    def test_e2e_error_handling(self):
        """E2E тест: обработка ошибочных запросов"""
        print("\n🔍 E2E Тест: Обработка ошибок")
        
        # Невалидный запрос
        invalid_notification = {"wrong": "data"}
        
        response = requests.post(f"{self.api_url}/notify", json=invalid_notification, timeout=5)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
        print(f"  ✅ Ошибка 400 обработана правильно")
        
        # Запрос с пустым телом
        response = requests.post(f"{self.api_url}/notify", json={}, timeout=5)
        self.assertEqual(response.status_code, 400)
        print(f"  ✅ Пустой запрос отклонён")
        
        print(f"  🎉 E2E тест ошибок пройден!")
    
    def test_e2e_multiple_channels(self):
        """E2E тест: отправка через разные каналы"""
        print("\n🔍 E2E Тест: Множественные каналы")
        
        channels = ["email", "sms", "telegram", "push"]
        
        for channel in channels:
            notification = {
                "channel": channel,
                "to": f"test@{channel}.com",
                "template": f"{channel}_test"
            }
            
            response = requests.post(f"{self.api_url}/notify", json=notification, timeout=5)
            self.assertEqual(response.status_code, 200)
            print(f"  ✅ Канал {channel} работает")
        
        print(f"  🎉 Все каналы протестированы!")


def run_e2e_tests():
    """Запуск всех E2E тестов с отчётом"""
    print("\n" + "="*60)
    print("E2E ТЕСТИРОВАНИЕ NOTIFICATION HUB")
    print("="*60)
    
    # Проверка доступности модулей
    modules = [
        ("API", "http://localhost:5001/queue"),
        ("Worker", "http://localhost:5002/process"),
        ("Логи", "http://localhost:5003/logs")
    ]
    
    all_available = True
    for name, url in modules:
        try:
            requests.get(url, timeout=2)
            print(f"✅ {name} доступен")
        except:
            print(f"❌ {name} НЕ ДОСТУПЕН")
            all_available = False
    
    if not all_available:
        print("\n⚠️ Запустите все модули перед выполнением E2E тестов!")
        return False
    
    # Запуск тестов
    suite = unittest.TestLoader().loadTestsFromTestCase(NotificationHubE2ETest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТ E2E ТЕСТИРОВАНИЯ:")
    print(f="=" * 40)
    print(f"✅ Пройдено: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Ошибок: {len(result.errors)}")
    print(f"⚠️ Провалено: {len(result.failures)}")
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_e2e_tests()
