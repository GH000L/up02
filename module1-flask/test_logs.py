import requests
import time
from loguru import logger

logger.info("=== Тестирование логирования ===")

# Успешный запрос
logger.info("Отправка успешного уведомления")
response = requests.post(
    "http://localhost:5001/notify",
    json={
        "channel": "email",
        "to": "test@example.com",
        "template": "welcome"
    }
)
logger.info(f"Ответ: {response.status_code} - {response.json()}")

# Ошибочный запрос (нет поля to)
logger.info("Отправка ошибочного уведомления")
response = requests.post(
    "http://localhost:5001/notify",
    json={
        "channel": "email",
        "template": "welcome"
    }
)
logger.info(f"Ответ: {response.status_code} - {response.json()}")

logger.success("Тестирование завершено")
