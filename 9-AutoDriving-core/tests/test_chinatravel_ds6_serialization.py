"""Serialization regression: NumPy integers must not become quoted room types."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_chinatravel_ds6 import native
import numpy as np

class SerializationTests(unittest.TestCase):
    def test_numeric_types_are_preserved(self):
        value=native({'room_type':np.int64(2),'cost':np.float64(32.5),'tickets':np.int32(4)})
        self.assertEqual(value,{'room_type':2,'cost':32.5,'tickets':4})
        self.assertIs(type(value['room_type']),int)

    def test_strings_are_not_silently_repaired(self):
        self.assertEqual(native({'room_type':'2'}),{'room_type':'2'})

    def test_nonfinite_and_unknown_values_fail(self):
        for value in [float('nan'),float('inf')]:
            with self.assertRaises(ValueError):native(value)
        with self.assertRaises(TypeError):native(object())

if __name__=='__main__':unittest.main()
