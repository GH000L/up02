#!/usr/bin/env python
"""
Запуск всех тестов: unit + интеграционные + E2E
"""

import subprocess
import sys

def run_tests():
    print("\n" + "="*60)
    print("ЗАПУСК ВСЕХ ТЕСТОВ")
    print("="*60)
    
    tests = [
        ("Unit тесты", "python tests/unit/test_adapters.py"),
        ("Интеграционные тесты", "python tests/integration/test_api_integration.py"),
        ("E2E тесты", "python tests/e2e/test_e2e_scenario.py")
    ]
    
    results = []
    for name, command in tests:
        print(f"\n📋 Запуск: {name}")
        print("-" * 40)
        result = subprocess.run(command, shell=True)
        results.append((name, result.returncode == 0))
    
    print("\n" + "="*60)
    print("ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"  {status} {name}")
    print("="*60)

if __name__ == "__main__":
    run_tests()
