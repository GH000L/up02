"""Адаптеры для тестов (копия из module5-orchestrator-saga)"""

class CartToOrderAdapter:
    @staticmethod
    def transform(cart_data):
        result = {
            "channel": cart_data.get("channel", "email"),
            "to": cart_data.get("to", ""),
            "template": cart_data.get("template", "default"),
            "data": {
                "original_id": cart_data.get("id", ""),
                "processed_by": "orchestrator"
            }
        }
        if "data" in cart_data and cart_data["data"]:
            result["data"].update(cart_data["data"])
        return result


class ResponseToLogAdapter:
    @staticmethod
    def transform(module_name, response_data, status_code=200):
        return {
            "module": module_name,
            "status_code": status_code,
            "response": response_data,
            "success": 200 <= status_code < 300
        }
