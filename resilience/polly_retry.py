"""
Аналог Polly для Python:
- Retry policy (повторные попытки)
- Circuit Breaker (предохранитель)
"""

import time
import requests
from functools import wraps
from loguru import logger
from datetime import datetime, timedelta

class CircuitBreaker:
    """Предохранитель — при 3 ошибках блокирует вызовы на 30 секунд"""
    
    def __init__(self, failure_threshold=3, timeout_seconds=30):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout_seconds):
                logger.info("Предохранитель переходит в HALF_OPEN состояние")
                self.state = "HALF_OPEN"
            else:
                logger.warning("Предохранитель OPEN — вызов заблокирован")
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                logger.info("Успешный вызов в HALF_OPEN — предохранитель закрывается")
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.error(f"Предохранитель OPEN после {self.failure_count} ошибок")
            
            raise e


def retry(max_attempts=3, delay=1, backoff=2):
    """Декоратор для повторных попыток с экспоненциальной задержкой"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    wait_time = delay * (backoff ** attempt)
                    logger.warning(f"Попытка {attempt + 1}/{max_attempts} не удалась: {e}. Ждём {wait_time}с...")
                    if attempt < max_attempts - 1:
                        time.sleep(wait_time)
            logger.error(f"Все {max_attempts} попыток не удались")
            raise last_exception
        return wrapper
    return decorator


# Примеры использования
if __name__ == "__main__":
    logger.info("=== Тестирование Retry Policy ===")
    
    # Эмуляция нестабильного сервиса
    unstable_service_calls = 0
    
    @retry(max_attempts=3, delay=1)
    def unstable_call():
        global unstable_service_calls
        unstable_service_calls += 1
        if unstable_service_calls < 2:
            logger.info(f"Вызов {unstable_service_calls}: эмулируем ошибку")
            raise Exception("Сервис временно недоступен")
        logger.info(f"Вызов {unstable_service_calls}: УСПЕХ!")
        return "OK"
    
    try:
        result = unstable_call()
        logger.success(f"Результат: {result}")
    except Exception as e:
        logger.error(f"Финальная ошибка: {e}")
    
    logger.info("\n=== Тестирование Circuit Breaker ===")
    
    breaker = CircuitBreaker(failure_threshold=2, timeout_seconds=10)
    
    def failing_call():
        logger.info("Вызов падающего сервиса...")
        raise Exception("Сервис не отвечает")
    
    def success_call():
        logger.info("Вызов работающего сервиса...")
        return "OK"
    
    # Первые 2 ошибки
    for i in range(2):
        try:
            breaker.call(failing_call)
        except Exception as e:
            logger.error(f"Ошибка {i+1}: {e}")
    
    # Проверяем состояние
    logger.info(f"Состояние предохранителя: {breaker.state}")
    
    # Следующий вызов должен быть заблокирован
    try:
        breaker.call(failing_call)
    except Exception as e:
        logger.error(f"Заблокировано: {e}")
    
    logger.info(f"Состояние предохранителя: {breaker.state}")
    
    # Ждём восстановления
    logger.info("Ждём 11 секунд для восстановления...")
    time.sleep(11)
    
    # Пробуем снова с успешным вызовом
    try:
        result = breaker.call(success_call)
        logger.success(f"После восстановления: {result}")
        logger.info(f"Состояние предохранителя: {breaker.state}")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
