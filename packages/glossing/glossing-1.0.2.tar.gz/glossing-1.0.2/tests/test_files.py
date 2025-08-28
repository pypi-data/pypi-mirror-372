import unittest
import os
from src.glossing import load_igt_file

class TestFiles(unittest.TestCase):
    toy_data_path = os.path.join(os.path.dirname(__file__), "toy-data.igt")

    def test_load_file(self):
        """Test that we can load IGT from a text file"""
        igts = load_igt_file(self.toy_data_path)
        self.assertEqual(len(igts), 4)
        self.assertEqual(igts[0].transcription, "I xkaj seche' ra lék'el rk'i rixóqil.")
        self.assertEqual(igts[1].segmentation, "x-pe man ánim x-ka-ye' ra lek'el r-k'i j-maam")
        self.assertEqual(igts[2].glosses, "CONJ COM-venir E3S-abuelo E3S-ver DIM niño")
        self.assertEqual(igts[3].translation, "Y crecio la mujer.")