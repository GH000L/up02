"""
Saga Orchestrator для сквозного сценария отправки уведомления
Шаги:
1. Сохранить в БД (шаг БД)
2. Поставить в очередь (шаг очередь)
3. Отправить через канал (шаг отправка)
4. Записать статус (шаг логи)

Если любой шаг失败了 — выполняются компенсации
"""

import requests
import time
from datetime import datetime
from loguru import logger
from state_machine import NotificationStateMachine

class NotificationSaga:
    """Оркестратор Saga для уведомлений"""
    
    def __init__(self):
        self.services = {
            "api": "http://localhost:5001",
            "worker": "http://localhost:5002",
            "logs": "http://localhost:5003",
            "db": "http://localhost:5004"
        }
        self.compensation_steps = []
        
    def execute_step(self, step_name, action_func, compensation_func):
        """Выполнить шаг с возможностью компенсации"""
        try:
            logger.info(f"▶️  Выполнение шага: {step_name}")
            result = action_func()
            if result and result.get("status") in ["ok", "success", "accepted", "created"]:
                logger.success(f"✅ Шаг выполнен: {step_name}")
                self.compensation_steps.append(compensation_func)
                return True
            else:
                logger.error(f"❌ Ошибка шага: {step_name} -> {result}")
                self._compensate()
                return False
        except Exception as e:
            logger.error(f"❌ Исключение в шаге {step_name}: {str(e)}")
            self._compensate()
            return False
    
    def _compensate(self):
        """Выполнить компенсации в обратном порядке"""
        logger.warning("⚠️ Запуск компенсаций...")
        for comp in reversed(self.compensation_steps):
            try:
                comp()
                logger.info("Компенсация выполнена")
            except Exception as e:
                logger.error(f"Ошибка компенсации: {e}")
    
    def send_notification_saga(self, notification_data, state_machine):
        """Полный Saga процесс отправки уведомления"""
        
        notification_id = None
        
        # Шаг 1: Отправить в API модуля 1
        def step1_action():
            nonlocal notification_id
            response = requests.post(
                f"{self.services['api']}/notify",
                json=notification_data,
                timeout=5
            )
            if response.status_code == 200:
                notification_id = response.json().get("notification_id")
                state_machine.notification_id = notification_id
                return {"status": "accepted", "id": notification_id}
            return None
        
        def step1_compensation():
            logger.info(f"Компенсация: удаляем уведомление {notification_id} из API")
            # В реальном API нет DELETE, просто логируем
            pass
        
        if not self.execute_step("API вызов", step1_action, step1_compensation):
            return False
        
        state_machine.queue()
        
        # Шаг 2: Поставить в очередь worker'а
        def step2_action():
            response = requests.post(
                f"{self.services['worker']}/task",
                json={
                    "id": notification_id,
                    "channel": notification_data.get("channel"),
                    "to": notification_data.get("to"),
                    "template": notification_data.get("template")
                },
                timeout=5
            )
            if response.status_code == 200:
                # Запускаем обработку
                requests.get(f"{self.services['worker']}/process", timeout=5)
                return {"status": "queued"}
            return None
        
        def step2_compensation():
            logger.info(f"Компенсация: удаляем задачу {notification_id} из очереди")
            # В реальности — удалить из очереди
            pass
        
        if not self.execute_step("Постановка в очередь", step2_action, step2_compensation):
            return False
        
        state_machine.start_sending()
        
        # Шаг 3: Записать в логи
        def step3_action():
            response = requests.post(
                f"{self.services['logs']}/log",
                json={
                    "notification_id": notification_id,
                    "channel": notification_data.get("channel"),
                    "status": "sent",
                    "sent_at": datetime.now().isoformat()
                },
                timeout=5
            )
            if response.status_code == 200:
                return {"status": "logged"}
            return None
        
        def step3_compensation():
            logger.info(f"Компенсация: удаляем лог {notification_id}")
        
        if not self.execute_step("Запись в логи", step3_action, step3_compensation):
            return False
        
        # Шаг 4: Сохранить в БД (если доступна)
        if self.services.get("db"):
            def step4_action():
                try:
                    response = requests.post(
                        f"{self.services['db']}/notifications",
                        json={
                            "channel_id": 1,  # email
                            "recipient": notification_data.get("to")
                        },
                        timeout=3
                    )
                    if response.status_code == 200:
                        return {"status": "saved_to_db"}
                except:
                    pass
                return None
            
            def step4_compensation():
                logger.info(f"Компенсация: удаляем запись из БД {notification_id}")
            
            self.execute_step("Сохранение в БД", step4_action, step4_compensation)
        
        state_machine.mark_sent()
        
        logger.success(f"🎉 Saga успешно завершена для уведомления {notification_id}")
        return True


def run_end_to_end_scenario():
    """Запуск сквозного сценария"""
    
    print("\n" + "="*60)
    print("СКВОЗНОЙ СЦЕНАРИЙ: ОТПРАВКА УВЕДОМЛЕНИЯ")
    print("="*60 + "\n")
    
    # Тестовое уведомление
    test_notification = {
        "channel": "email",
        "to": "end-to-end@test.com",
        "template": "e2e_test",
        "data": {
            "test_id": "SCENARIO_001",
            "message": "Сквозной тест уведомления"
        }
    }
    
    state_machine = NotificationStateMachine("pending-id")
    saga = NotificationSaga()
    
    logger.info(f"📨 Входные данные: {test_notification}")
    
    success = saga.send_notification_saga(test_notification, state_machine)
    
    print("\n" + "="*60)
    print("РЕЗУЛЬТАТ СКВОЗНОГО СЦЕНАРИЯ:")
    print(f"Статус: {'УСПЕШНО ✅' if success else 'ОШИБКА ❌'}")
    print(f"Состояние State Machine: {state_machine.get_status()}")
    print("="*60 + "\n")
    
    return success, state_machine


if __name__ == "__main__":
    # Проверка доступности сервисов
    print("Проверка доступности модулей...")
    saga = NotificationSaga()
    for name, url in saga.services.items():
        try:
            response = requests.get(f"{url}/", timeout=2)
            print(f"  ✅ {name}: {url}")
        except:
            print(f"  ❌ {name}: {url} - НЕ ДОСТУПЕН")
    
    print("\n")
    run_end_to_end_scenario()
