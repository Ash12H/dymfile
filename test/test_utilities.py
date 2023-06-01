import unittest
import logging

from dymfiles.core.utilities import date_dym2tostr


class Test_utilities(unittest.TestCase):
    def test_date_dym2tostr(self):
        logging.disable()
        # print("\nThe function date_dym2tostr has a strange behaviour:")
        # print(f"date_dym2tostr(2022.0) = {date_dym2tostr(2022.0)}")
        # print(f"date_dym2tostr(2022.001) = {date_dym2tostr(2022.001)}")
        # print(f"date_dym2tostr(2021.999) = {date_dym2tostr(2021.999)}")
        # print(f"date_dym2tostr(2022.0014) = {date_dym2tostr(2022.0014)}")
        self.assertEqual(date_dym2tostr(-2021.512), "xxxxxxxx")
        with self.assertRaises(TypeError):
            date_dym2tostr("invalid")
