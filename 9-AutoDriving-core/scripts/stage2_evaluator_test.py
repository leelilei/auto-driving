"""Official schema, hard-constraint, invalid-input and denominator validation.
Run with external/ChinaTravel/.venv-chinatravel/bin/python.
"""
import sys
import unittest
from pathlib import Path
if __name__ == '__main__':
    tests=Path(__file__).resolve().parents[1]/'tests'
    suite=unittest.defaultTestLoader.discover(str(tests),pattern='test_chinatravel_pipeline.py')
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
