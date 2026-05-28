"""
Интеграционный оркестратор
Вызывает модули: Notification API (5001) -> Worker (5002) -> Logs (5003)
"""

import requests
import time
from datetime import datetime
from logger_config import logger
from adapters import CartToOrderAdapter, ResponseToLogAdapter

class IntegrationOrchestrator:
    """Оркестратор вызовов между модулями"""
    
    def __init__(self):
        self.module_urls = {
            "notification_api": "http://localhost:5001",
            "worker": "http://localhost:5002",
            "logs_api": "http://localhost:5003"
        }
        self.timeout = 10
        self.retry_count = 2
        
    def call_module(self, module_name, method, endpoint, data=None):
        """Универсальный вызов HTTP модуля"""
        url = f"{self.module_urls[module_name]}{endpoint}"
        
        logger.info(f"Вызов {module_name}: {method} {url}")
        if data:
            logger.debug(f"Данные: {data}")
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=self.timeout)
            else:
                response = requests.post(url, json=data, timeout=self.timeout)
                
            log_data = ResponseToLogAdapter.transform(module_name, response.text, response.status_code)
            logger.info(f"Ответ {module_name}: статус {response.status_code}")
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка вызова {module_name}: {str(e)}")
            return None
    
    def send_notification(self, notification_data):
        """
        Полный процесс отправки уведомления через все модули:
        1. Вызвать API (модуль 1) -> положить в очередь
        2. Вызвать Worker (модуль 2) -> обработать задачу
        3. Записать в логи (модуль 3)
        """
        logger.info("=" * 50)
        logger.info(f"Начало интеграции: отправка уведомления")
        
        # Шаг 1: Отправка в Notification API (модуль 1)
        logger.info("Шаг 1: Вызов Notification API (порт 5001)")
        response1 = self.call_module("notification_api", "POST", "/notify", notification_data)
        
        if not response1 or response1.status_code != 200:
            logger.error("Не удалось отправить уведомление в API")
            return {"status": "error", "step": "api_call", "error": "API не ответил"}
        
        result = response1.json()
        notification_id = result.get("notification_id")
        logger.success(f"Уведомление принято, ID: {notification_id}")
        
        # Шаг 2: Обработка через Worker (модуль 2)
        logger.info("Шаг 2: Вызов Worker для обработки (порт 5002)")
        
        # Сначала передаём задачу в worker
        task_data = {
            "id": notification_id,
            "channel": notification_data.get("channel"),
            "to": notification_data.get("to"),
            "template": notification_data.get("template"),
            "data": notification_data.get("data", {})
        }
        
        response2 = self.call_module("worker", "POST", "/task", task_data)
        
        if response2 and response2.status_code == 200:
            # Запускаем обработку одной задачи
            response_process = self.call_module("worker", "GET", "/process")
            if response_process and response_process.status_code == 200:
                process_result = response_process.json()
                logger.success(f"Worker обработал задачу: {process_result}")
        
        # Шаг 3: Запись в логи (модуль 3)
        logger.info("Шаг 3: Запись в логи (порт 5003)")
        
        log_entry = {
            "notification_id": notification_id,
            "channel": notification_data.get("channel"),
            "status": "processed_by_orchestrator",
            "sent_at": datetime.now().isoformat(),
            "error": ""
        }
        
        response3 = self.call_module("logs_api", "POST", "/log", log_entry)
        
        if response3 and response3.status_code == 200:
            logger.success("Статус записан в логи")
        
        logger.success(f"Интеграция завершена для ID: {notification_id}")
        logger.info("=" * 50)
        
        return {
            "status": "success",
            "notification_id": notification_id,
            "steps": {
                "api": response1.status_code if response1 else None,
                "worker": response2.status_code if response2 else None,
                "logs": response3.status_code if response3 else None
            }
        }
    
    def process_batch(self, notifications_list):
        """Обработка пакета уведомлений"""
        results = []
        for i, notification in enumerate(notifications_list):
            logger.info(f"Обработка {i+1}/{len(notifications_list)}")
            result = self.send_notification(notification)
            results.append(result)
            time.sleep(0.5)  # небольшая задержка
        return results


def main():
    """Точка входа - демонстрация работы оркестратора"""
    print("\n" + "="*60)
    print("ИНТЕГРАЦИОННЫЙ ОРКЕСТРАТОР - Notification Hub")
    print("="*60 + "\n")
    
    orchestrator = IntegrationOrchestrator()
    
    # Тестовое уведомление
    test_notification = {
        "channel": "email",
        "to": "test@integration.com",
        "template": "orchestrator_test",
        "data": {
            "name": "Тестовый пользователь",
            "message": "Это уведомление отправлено через оркестратор"
        }
    }
    
    print("📨 Отправка тестового уведомления через оркестратор...\n")
    
    result = orchestrator.send_notification(test_notification)
    
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТ ОРКЕСТРАЦИИ:")
    print(f"Статус: {result.get('status')}")
    print(f"ID уведомления: {result.get('notification_id')}")
    print(f"Шаги: {result.get('steps')}")
    print("="*60 + "\n")
    
    # Проверим логи
    print("📋 Проверка логов (модуль 3):")
    try:
        response = requests.get("http://localhost:5003/logs")
        if response.status_code == 200:
            logs = response.json()
            print(f"Всего записей в логах: {len(logs)}")
            for log in logs[-3:]:  # последние 3
                print(f"  - {log}")
    except:
        print("  Не удалось получить логи")
    
    return result


if __name__ == "__main__":
    main()
