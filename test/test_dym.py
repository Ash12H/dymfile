import logging
import os
import unittest

from dymfile.core.dym import get_file_format


# sys.path.insert(0, ".")


# ! WARNING Jules : I am not sure that DYMZ format is in use at the moment.
def create_dym_file(filepath: str, format: str):
    acceptable_dym_format = ("DYM2", "DYM3")
    if format not in acceptable_dym_format:
        raise ValueError(f"format must be one of {acceptable_dym_format}")
    with open(filepath, "w") as dymfile:
        dymfile.write(format)


class Test_dym(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.info("Création des fichiers dym pour le test du format.")
        create_dym_file("dym2file.dym", "DYM2")
        create_dym_file("dym3file.dym", "DYM3")

    @classmethod
    def tearDownClass(cls):
        logging.info("Destruction des fichiers dym.")
        for filename in ["dym2file.dym", "dym3file.dym"]:
            try:
                os.remove(filename)
            except Exception as e:
                logging.warning(f"Failed to delete {filename}. Reason: {e}")

    def test_get_file_format(self):
        self.assertEqual(
            get_file_format("dym2file.dym"),
            "DYM2",
        )
        self.assertEqual(
            get_file_format("dym3file.dym"),
            "DYM3",
        )
