import requests
import time
from orchestrator import IntegrationOrchestrator

def test_all_modules_available():
    """Проверка доступности всех модулей"""
    orchestrator = IntegrationOrchestrator()
    
    modules_status = {}
    for name, url in orchestrator.module_urls.items():
        try:
            response = requests.get(f"{url}/")
            modules_status[name] = "доступен"
        except:
            modules_status[name] = "НЕ ДОСТУПЕН"
    
    print("Статус модулей:")
    for name, status in modules_status.items():
        print(f"  {name}: {status}")
    
    return all(s == "доступен" for s in modules_status.values())

def test_orchestrator():
    """Тест оркестратора с несколькими уведомлениями"""
    print("\n=== ЗАПУСК ТЕСТА ОРКЕСТРАТОРА ===\n")
    
    orchestrator = IntegrationOrchestrator()
    
    test_notifications = [
        {
            "channel": "email",
            "to": "user1@test.com",
            "template": "test1",
            "data": {"name": "User1"}
        },
        {
            "channel": "sms",
            "to": "+79991234567",
            "template": "test2",
            "data": {"code": "123456"}
        },
        {
            "channel": "telegram",
            "to": "@testuser",
            "template": "test3",
            "data": {"message": "Hello from orchestrator"}
        }
    ]
    
    results = orchestrator.process_batch(test_notifications)
    
    success_count = sum(1 for r in results if r.get("status") == "success")
    print(f"\nРезультат: {success_count}/{len(results)} успешно")
    
    return results

if __name__ == "__main__":
    if test_all_modules_available():
        test_orchestrator()
    else:
        print("ОШИБКА: Запусти сначала все модули:")
        print("  1. module1-flask: python app.py")
        print("  2. module2-nodejs: node worker.js")
        print("  3. module3-python: python logs.py")
