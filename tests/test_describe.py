import unittest
import lxml.etree as etree
import subprocess

from tests.common import validate, server_wps_url


class DescribeTest(unittest.TestCase):

    def setUp(self):
        self.url = server_wps_url + '?service=wps&request=describeprocess&version=1.0.0&identifier=all'
        self.schema_url = 'http://schemas.opengis.net/wps/1.0.0/wpsDescribeProcess_response.xsd'

    def test_valid(self):
        assert validate(self.url, self.schema_url)


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(DescribeTest),
    ]
    return unittest.TestSuite(suite_list)
