import unittest
import requests
import time

class TestNotificationHubIntegration(unittest.TestCase):
    """Интеграционные тесты для Notification Hub API"""
    
    @classmethod
    def setUpClass(cls):
        """Проверка доступности сервисов перед тестами"""
        cls.api_url = "http://localhost:5001"
        cls.worker_url = "http://localhost:5002"
        cls.logs_url = "http://localhost:5003"
        
        # Ждём запуска сервисов
        time.sleep(2)
    
    def test_api_is_alive(self):
        """Тест: API модуль доступен"""
        response = requests.get(f"{self.api_url}/queue", timeout=5)
        self.assertEqual(response.status_code, 200)
    
    def test_worker_is_alive(self):
        """Тест: Worker модуль доступен"""
        response = requests.get(f"{self.worker_url}/process", timeout=5)
        self.assertEqual(response.status_code, 200)
    
    def test_logs_is_alive(self):
        """Тест: Логи модуль доступен"""
        response = requests.get(f"{self.logs_url}/logs", timeout=5)
        self.assertEqual(response.status_code, 200)
    
    def test_send_notification_success(self):
        """Интеграционный тест: отправка успешного уведомления"""
        notification = {
            "channel": "email",
            "to": "integration@test.com",
            "template": "test_template",
            "data": {"test": "integration"}
        }
        
        response = requests.post(f"{self.api_url}/notify", json=notification, timeout=5)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("notification_id", response.json())
        self.assertIn("status", response.json())
    
    def test_send_notification_missing_field(self):
        """Интеграционный тест: отправка с отсутствующим полем"""
        notification = {
            "channel": "email"
            # отсутствует поле 'to'
        }
        
        response = requests.post(f"{self.api_url}/notify", json=notification, timeout=5)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
    
    def test_send_notification_invalid_channel(self):
        """Интеграционный тест: неверный канал"""
        notification = {
            "channel": "invalid_channel",
            "to": "test@test.com",
            "template": "test"
        }
        
        response = requests.post(f"{self.api_url}/notify", json=notification, timeout=5)
        
        # API принимает любой канал (валидация на уровне worker)
        self.assertEqual(response.status_code, 200)
    
    def test_queue_endpoint(self):
        """Интеграционный тест: проверка очереди"""
        response = requests.get(f"{self.api_url}/queue", timeout=5)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("queue", response.json())
        self.assertIn("count", response.json())
    
    def test_logs_endpoint(self):
        """Интеграционный тест: проверка логов"""
        response = requests.get(f"{self.logs_url}/logs", timeout=5)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

class TestEndToEndFlow(unittest.TestCase):
    """Интеграционный тест: сквозной сценарий"""
    
    def test_full_notification_flow(self):
        """E2E: отправка -> очередь -> лог"""
        
        # Шаг 1: Отправка уведомления
        notification = {
            "channel": "email",
            "to": "e2e@test.com",
            "template": "e2e_test"
        }
        
        send_response = requests.post("http://localhost:5001/notify", json=notification, timeout=5)
        self.assertEqual(send_response.status_code, 200)
        
        notification_id = send_response.json().get("notification_id")
        self.assertIsNotNone(notification_id)
        
        # Шаг 2: Проверка очереди
        queue_response = requests.get("http://localhost:5001/queue", timeout=5)
        self.assertEqual(queue_response.status_code, 200)
        
        # Шаг 3: Обработка через worker
        process_response = requests.get("http://localhost:5002/process", timeout=5)
        self.assertEqual(process_response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
