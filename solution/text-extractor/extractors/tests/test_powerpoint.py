import unittest

from . import FileComparisonMixin


class TestPowerPointExtractor(unittest.TestCase, FileComparisonMixin):
    def test_pptx(self):
        self._test_file_type("pptx")
