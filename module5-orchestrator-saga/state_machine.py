"""
State Machine для уведомления
Статусы: 
NEW → QUEUED → SENDING → SENT → DELIVERED
                ↓
              FAILED → RETRY → SENDING (retry)
"""

from enum import Enum
from datetime import datetime
from loguru import logger

class NotificationState(Enum):
    NEW = "new"                    # Только создано
    QUEUED = "queued"              # В очереди
    SENDING = "sending"            # Отправляется
    SENT = "sent"                  # Отправлено (на почту/SMS и т.д.)
    DELIVERED = "delivered"        # Доставлено (получатель получил)
    FAILED = "failed"              # Ошибка
    RETRY = "retry"                # Повторная попытка
    CANCELLED = "cancelled"        # Отменено

class NotificationStateMachine:
    """Конечный автомат для уведомления"""
    
    def __init__(self, notification_id):
        self.notification_id = notification_id
        self.state = NotificationState.NEW
        self.history = []
        self.retry_count = 0
        self.max_retries = 3
        self._add_to_history("created")
    
    def _add_to_history(self, action):
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "from_state": self.state.value,
            "action": action
        })
    
    def can_transition(self, new_state):
        """Проверка разрешённых переходов"""
        transitions = {
            NotificationState.NEW: [NotificationState.QUEUED, NotificationState.CANCELLED],
            NotificationState.QUEUED: [NotificationState.SENDING, NotificationState.CANCELLED],
            NotificationState.SENDING: [NotificationState.SENT, NotificationState.FAILED],
            NotificationState.SENT: [NotificationState.DELIVERED, NotificationState.FAILED],
            NotificationState.DELIVERED: [],  # терминальное состояние
            NotificationState.FAILED: [NotificationState.RETRY, NotificationState.CANCELLED],
            NotificationState.RETRY: [NotificationState.SENDING, NotificationState.FAILED],
            NotificationState.CANCELLED: []   # терминальное состояние
        }
        return new_state in transitions.get(self.state, [])
    
    def transition_to(self, new_state):
        if not self.can_transition(new_state):
            logger.warning(f"Недопустимый переход {self.state.value} -> {new_state.value}")
            return False
        
        old_state = self.state
        self.state = new_state
        self._add_to_history(f"transition: {old_state.value} -> {new_state.value}")
        logger.info(f"StateMachine [{self.notification_id}]: {old_state.value} -> {new_state.value}")
        return True
    
    def queue(self):
        return self.transition_to(NotificationState.QUEUED)
    
    def start_sending(self):
        return self.transition_to(NotificationState.SENDING)
    
    def mark_sent(self):
        return self.transition_to(NotificationState.SENT)
    
    def mark_delivered(self):
        return self.transition_to(NotificationState.DELIVERED)
    
    def mark_failed(self):
        return self.transition_to(NotificationState.FAILED)
    
    def retry(self):
        if self.retry_count < self.max_retries:
            self.retry_count += 1
            logger.info(f"Попытка {self.retry_count}/{self.max_retries} для {self.notification_id}")
            return self.transition_to(NotificationState.RETRY)
        else:
            logger.error(f"Превышено число попыток для {self.notification_id}")
            return False
    
    def cancel(self):
        return self.transition_to(NotificationState.CANCELLED)
    
    def get_status(self):
        return {
            "notification_id": self.notification_id,
            "state": self.state.value,
            "retry_count": self.retry_count,
            "history": self.history[-5:]  # последние 5 событий
        }


# Пример использования
if __name__ == "__main__":
    sm = NotificationStateMachine("test-123")
    sm.queue()
    sm.start_sending()
    sm.mark_sent()
    sm.mark_delivered()
    print(sm.get_status())
