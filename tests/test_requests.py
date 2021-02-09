import unittest
import os

from tests.common import validate_file

class RequestsTest(unittest.TestCase):

    def test_valid_request(self):

        def valid_request(url, dirname, fname):
            fullpath = os.path.join(dirname, fname)
            if os.path.isfile(fullpath) and \
              not fname.startswith('.'):
                valid = validate_file(fullpath, url)
                self.assertTrue(valid, "%s requests valid" % fullpath)

        url = 'http://schemas.opengis.net/wps/1.0.0/wpsAll.xsd'
        for (dirpath, dirnames, filenames) in os.walk(os.path.join('static', 'requests')):
            for filename in filenames:
                valid_request(url, dirpath, filename)


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(RequestsTest),
    ]
    return unittest.TestSuite(suite_list)
