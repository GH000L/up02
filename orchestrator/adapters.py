"""
Адаптеры для преобразования данных между модулями
Аналог AutoMapper в C#
"""

class CartToOrderAdapter:
    """Преобразует данные из корзины в заказ"""
    
    @staticmethod
    def transform(cart_data):
        """
        Вход: данные из модуля корзины (или просто входящее уведомление)
        Выход: данные для модуля заказа
        """
        # Пример маппинга: входные данные -> нужная структура
        result = {
            "channel": cart_data.get("channel", "email"),
            "to": cart_data.get("to", ""),
            "template": cart_data.get("template", "default"),
            "data": {
                "original_id": cart_data.get("id", ""),
                "processed_by": "orchestrator"
            }
        }
        
        # Если есть дополнительные данные - пробрасываем
        if "data" in cart_data and cart_data["data"]:
            result["data"].update(cart_data["data"])
            
        return result


class ResponseToLogAdapter:
    """Преобразует ответы модулей в формат для логов"""
    
    @staticmethod
    def transform(module_name, response_data, status_code=200):
        return {
            "module": module_name,
            "status_code": status_code,
            "response": response_data,
            "success": 200 <= status_code < 300
        }
