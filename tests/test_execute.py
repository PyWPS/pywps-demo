"""Test various processes
"""
import unittest
import lxml.etree as etree
import time

from tests.common import validate, URL, get_response

from tests.common import NAMESPACES

class SayHello(unittest.TestCase):
    """Test sayhello process
    """

    def setUp(self):

        self.schema_url = 'http://schemas.opengis.net/wps/1.0.0/wpsExecute_response.xsd'


    def test_valid(self):
        "GET Execute request"

        url = URL + '?service=wps&request=execute&identifier=say_hello&version=1.0.0&datainputs=name=ahoj'
        assert validate(url, self.schema_url)

    def test_valid_lineage(self):
        "GET Execute request, lineage=true"

        url = URL + '?service=wps&request=execute&identifier=say_hello&version=1.0.0&datainputs=name=ahoj&lineage=true'
        assert validate(url, self.schema_url)

class Buffer(unittest.TestCase):
    """Test buffer process
    """

    def setUp(self):

        self.schema_url = 'http://schemas.opengis.net/wps/1.0.0/wpsExecute_response.xsd'
        self.url = URL
        resp = get_response('http://localhost:5000/static/requests/execute_buffer_post.xml')
        self.request_data = resp.read()

    def test_valid(self):
        "POST Execute request"

        assert validate(self.url, self.schema_url, self.request_data)


    #def test_valid_lineage(self):
    #    "GET Execute Buffer"

    #    assert validate(url, self.schema_url)

class SyncAndAsync(unittest.TestCase):
    """Test buffer sync and async
    """

    def _get_request(self, url):

        request = get_response(url)
        request_data = request.read()
        return request_data

    def _get_response(self, request):

        response = get_response(URL, request)
        response_data = response.read()
        response_doc = etree.fromstring(response_data)

        return response_doc

    def test_sync(self):
        request = self._get_request('http://localhost:5000/static/requests/execute_buffer_post.xml')
        response = self._get_response(request)

        self.assertEqual(
            response.xpath('//wps:ExecuteResponse/wps:Process/ows:Identifier',
                namespaces=NAMESPACES)[0].text, 'buffer')

        self.assertEqual(
            response.xpath(
                '//wps:ExecuteResponse/wps:Status/wps:ProcessSucceeded',
                namespaces=NAMESPACES)[0].text,
            'PyWPS Process GDAL Buffer process finished')

        self.assertEqual(len(response.xpath(
            '//wps:ExecuteResponse/wps:ProcessOutputs/wps:Output',
                namespaces=NAMESPACES)), 1)

        self.assertEqual(response.xpath(
            '//wps:ExecuteResponse/wps:ProcessOutputs/'
            'wps:Output/wps:Data/wps:ComplexData',
                namespaces=NAMESPACES)[0].get('mimeType'),
                'application/gml+xml')

        self.assertTrue(response.xpath(
            '//wps:ExecuteResponse/wps:ProcessOutputs/wps:Output/wps:Data/'
            'wps:ComplexData/ogr:FeatureCollection',
            namespaces=NAMESPACES))

    def test_sync_reference(self):
        request = self._get_request('http://localhost:5000/static/requests/execute_buffer_sync_reference.xml')
        response = self._get_response(request)

        self.assertEqual(
            response.xpath('//wps:ExecuteResponse/wps:Process/ows:Identifier',
                           namespaces=NAMESPACES)[0].text, 'buffer')

        self.assertEqual(
            response.xpath(
                '//wps:ExecuteResponse/wps:Status/wps:ProcessSucceeded',
                namespaces=NAMESPACES)[0].text,
            'PyWPS Process GDAL Buffer process finished')

        self.assertEqual(len(response.xpath(
            '//wps:ExecuteResponse/wps:ProcessOutputs/wps:Output',
            namespaces=NAMESPACES)), 1)

        self.assertEqual(response.xpath(
            '//wps:ExecuteResponse/wps:ProcessOutputs/'
            'wps:Output/wps:Reference',
            namespaces=NAMESPACES)[0].get('mimeType'),
                         'application/gml+xml')

        self.assertTrue(response.xpath(
            '//wps:ExecuteResponse/wps:ProcessOutputs/wps:Output/'
            'wps:Reference',
            namespaces=NAMESPACES))

        data_href = response.xpath(
            '//wps:ExecuteResponse/wps:ProcessOutputs/wps:Output/'
            'wps:Reference',
            namespaces=NAMESPACES)[0].get('href')

        data = self._get_request(data_href)
        data_doc = etree.fromstring(data)

        self.assertTrue(data_doc.xpath('//ogr:FeatureCollection',
                                       namespaces=NAMESPACES))

    def test_async(self):
        """
        This test fails for Docker. Docker supports only referenced output in response.
        """
        request = self._get_request('http://localhost:5000/static/requests/execute_buffer_async.xml')
        response = self._get_response(request)

        self.assertEqual(
            response.xpath('//wps:ExecuteResponse/wps:Process/ows:Identifier',
                namespaces=NAMESPACES)[0].text, 'buffer')

        self.assertTrue(response.xpath(
            '//wps:ExecuteResponse/wps:Status/wps:ProcessAccepted',
                namespaces=NAMESPACES))

        status_location = response.xpath(
            '//wps:ExecuteResponse',
            namespaces=NAMESPACES)[0].get('statusLocation')
        self.assertTrue(status_location)

        time.sleep(1) # make sure, buffer is done
        status = self._get_request(status_location)
        status_doc = etree.fromstring(status)

        self.assertTrue(status_doc.xpath(
            '//wps:ExecuteResponse/wps:Status/wps:ProcessSucceeded',
                namespaces=NAMESPACES))

        self.assertTrue(status_doc.xpath(
            '//wps:ExecuteResponse/wps:ProcessOutputs/wps:Output/wps:Data/'
            'wps:ComplexData/ogr:FeatureCollection',
            namespaces=NAMESPACES))

    def test_async_reference(self):
        request = self._get_request('http://localhost:5000/static/requests/execute_buffer_async_reference.xml')
        response = self._get_response(request)

        self.assertTrue(response.xpath(
            '//wps:ExecuteResponse/wps:Status/wps:ProcessAccepted',
                namespaces=NAMESPACES))

        status_location = response.xpath(
            '//wps:ExecuteResponse',
            namespaces=NAMESPACES)[0].get('statusLocation')
        self.assertTrue(status_location)

        time.sleep(1) # make sure, buffer is done
        status = self._get_request(status_location)
        status_doc = etree.fromstring(status)

        self.assertTrue(status_doc.xpath(
            '//wps:ExecuteResponse/wps:Status/wps:ProcessSucceeded',
                namespaces=NAMESPACES))

        self.assertTrue(status_doc.xpath(
            '//wps:ExecuteResponse/wps:ProcessOutputs/wps:Output/'
            'wps:Reference',
            namespaces=NAMESPACES))

        self.assertEqual(status_doc.xpath(
            '//wps:ExecuteResponse/wps:ProcessOutputs/wps:Output/'
            'wps:Reference',
            namespaces=NAMESPACES)[0].get('mimeType'), 'application/gml+xml')

        data_href = status_doc.xpath(
            '//wps:ExecuteResponse/wps:ProcessOutputs/wps:Output/'
            'wps:Reference',
            namespaces=NAMESPACES)[0].get('href')

        data = self._get_request(data_href)
        data_doc = etree.fromstring(data)

        self.assertTrue(data_doc.xpath('//ogr:FeatureCollection',
            namespaces=NAMESPACES))


def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(SayHello),
        loader.loadTestsFromTestCase(Buffer)
    ]
    return unittest.TestSuite(suite_list)
