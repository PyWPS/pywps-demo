import unittest

from tests.common import validate, server_wps_url


class CapabilitiesTest(unittest.TestCase):

    def setUp(self):
        self.url = server_wps_url + "?service=wps&request=getcapabilities"
        self.schema_url = 'http://schemas.opengis.net/wps/1.0.0/wpsGetCapabilities_response.xsd'

    def test_valid(self):
        assert validate(self.url, self.schema_url)


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(CapabilitiesTest),
    ]
    return unittest.TestSuite(suite_list)
