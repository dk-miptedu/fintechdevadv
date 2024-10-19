import unittest

# Автоматическое обнаружение и запуск всех тестов в директории tests
if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
