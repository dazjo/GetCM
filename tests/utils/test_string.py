from unittest import TestCase
from getcm.utils.string import *

class TestStringUtils(TestCase):
    def test_convert_bytes(self):
        assert convert_bytes(1024) == '1.00 KB'
        assert convert_bytes(1100) == '1.07 KB'
        assert convert_bytes(1024 ** 2) == '1.00 MB'
        assert convert_bytes(1024 ** 3) == '1.00 GB'
        assert convert_bytes(1024 ** 4) == '1.00 TB'

    def test_base62_encode(self):
        assert base62_encode(1234) == 'jU'

    def test_base62_decode(self):
        assert base62_decode('jU') == 1234
