import logging
import os
import unittest

from dymfile.core.dym import get_file_format

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ABSOLUTE_PATH_TO_TEST_DATA = os.path.join(THIS_DIR, "test_dym/")


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
        create_dym_file(
            os.path.join(ABSOLUTE_PATH_TO_TEST_DATA, "dym2file.dym"), "DYM2"
        )
        create_dym_file(
            os.path.join(ABSOLUTE_PATH_TO_TEST_DATA, "dym3file.dym"), "DYM3"
        )

    @classmethod
    def tearDownClass(cls):
        logging.info("Destruction des fichiers dym.")
        for filename in os.listdir(ABSOLUTE_PATH_TO_TEST_DATA):
            file_path = os.path.join(ABSOLUTE_PATH_TO_TEST_DATA, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                logging.warning(f"Failed to delete {file_path}. Reason: {e}")

    def test_get_file_format(self):
        self.assertEqual(
            get_file_format(
                os.path.join(ABSOLUTE_PATH_TO_TEST_DATA, "dym2file.dym")
            ),
            "DYM2",
        )
        self.assertEqual(
            get_file_format(
                os.path.join(ABSOLUTE_PATH_TO_TEST_DATA, "dym3file.dym")
            ),
            "DYM3",
        )
