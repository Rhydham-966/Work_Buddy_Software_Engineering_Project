import unittest
import sys

def run():
    loader = unittest.TestLoader()
    suite = loader.discover('tests')
    
    with open('clean_test_output.txt', 'w', encoding='utf-8') as f:
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        runner.run(suite)

if __name__ == '__main__':
    run()
