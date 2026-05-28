import unittest
import sys
sys.path.append('../../module5-orchestrator-saga')

class TestCartToOrderAdapter(unittest.TestCase):
    """Unit-тесты для адаптера трансформации данных"""
    
    def test_transform_valid_data(self):
        """Тест: корректная трансформация данных"""
        from adapters import CartToOrderAdapter
        
        input_data = {
            "channel": "email",
            "to": "test@example.com",
            "template": "welcome",
            "data": {"name": "John"}
        }
        
        result = CartToOrderAdapter.transform(input_data)
        
        self.assertEqual(result["channel"], "email")
        self.assertEqual(result["to"], "test@example.com")
        self.assertEqual(result["template"], "welcome")
        self.assertIn("original_id", result["data"])
    
    def test_transform_missing_fields(self):
        """Тест: обработка отсутствующих полей"""
        from adapters import CartToOrderAdapter
        
        input_data = {"channel": "sms"}
        
        result = CartToOrderAdapter.transform(input_data)
        
        self.assertEqual(result["to"], "")
        self.assertEqual(result["template"], "default")
    
    def test_transform_with_custom_data(self):
        """Тест: проброс дополнительных данных"""
        from adapters import CartToOrderAdapter
        
        input_data = {
            "channel": "telegram",
            "to": "@user",
            "data": {"custom_field": "value", "priority": "high"}
        }
        
        result = CartToOrderAdapter.transform(input_data)
        
        self.assertEqual(result["data"]["custom_field"], "value")
        self.assertEqual(result["data"]["priority"], "high")

class TestResponseToLogAdapter(unittest.TestCase):
    """Unit-тесты для адаптера логов"""
    
    def test_transform_success_response(self):
        """Тест: трансформация успешного ответа"""
        from adapters import ResponseToLogAdapter
        
        result = ResponseToLogAdapter.transform("api", '{"status":"ok"}', 200)
        
        self.assertEqual(result["module"], "api")
        self.assertEqual(result["status_code"], 200)
        self.assertTrue(result["success"])
    
    def test_transform_error_response(self):
        """Тест: трансформация ошибочного ответа"""
        from adapters import ResponseToLogAdapter
        
        result = ResponseToLogAdapter.transform("worker", '{"error":"timeout"}', 500)
        
        self.assertEqual(result["status_code"], 500)
        self.assertFalse(result["success"])

if __name__ == '__main__':
    unittest.main()
