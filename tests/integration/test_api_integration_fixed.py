import unittest
import requests
import sys

class TestNotificationHubIntegration(unittest.TestCase):
    """Интеграционные тесты (требуют запущенных модулей)"""
    
    @classmethod
    def setUpClass(cls):
        cls.api_url = "http://localhost:5001"
        cls.worker_url = "http://localhost:5002"
        cls.logs_url = "http://localhost:5003"
        
        # Проверяем, запущены ли модули
        try:
            requests.get(f"{cls.api_url}/queue", timeout=2)
            cls.modules_available = True
        except:
            cls.modules_available = False
            print("⚠️ Модули не запущены, пропускаем интеграционные тесты")
    
    def test_api_alive(self):
        if not self.modules_available:
            self.skipTest("Модули не запущены")
        response = requests.get(f"{self.api_url}/queue", timeout=5)
        self.assertEqual(response.status_code, 200)
    
    def test_worker_alive(self):
        if not self.modules_available:
            self.skipTest("Модули не запущены")
        response = requests.get(f"{self.worker_url}/process", timeout=5)
        self.assertEqual(response.status_code, 200)
    
    def test_logs_alive(self):
        if not self.modules_available:
            self.skipTest("Модули не запущены")
        response = requests.get(f"{self.logs_url}/logs", timeout=5)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
