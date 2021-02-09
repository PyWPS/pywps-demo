"""Test various processes
"""
import unittest
import lxml.etree as etree
import time

from tests.common import NAMESPACES, validate, server_wps_url, server_base_url, get_response, schema_wps_url


process_succeeded = '//wps:ExecuteResponse/wps:Status/wps:ProcessSucceeded'
process_identifier = '//wps:ExecuteResponse/wps:Process/ows:Identifier'
process_accepted = '//wps:ExecuteResponse/wps:Status/wps:ProcessAccepted'
process_outputs = '//wps:ExecuteResponse/wps:ProcessOutputs/wps:Output'
process_outputs_reference = process_outputs+'/wps:Reference'


class SayHello(unittest.TestCase):
    """
    Test sayhello process
    """

    def setUp(self):
        self.schema_url = schema_wps_url

    def test_valid(self):
        """GET Execute request"""

        url = server_wps_url + '?service=wps&request=execute&identifier=say_hello&version=1.0.0&datainputs=name=ahoj'
        assert validate(url, self.schema_url)


class Buffer(unittest.TestCase):
    """
    Test buffer process
    """

    def setUp(self):
        self.schema_url = schema_wps_url
        self.url = server_wps_url
        resp = get_response(server_base_url + '/static/requests/buffer.xml')
        self.request_data = resp.read()

    def test_valid(self):
        """"POST Execute request"""

        validate(self.url, self.schema_url, self.request_data)


class SyncAndAsync(unittest.TestCase):
    """
    Test buffer sync and async
    """

    def _get_request(self, url):
        request = get_response(url)
        request_data = request.read()
        return request_data

    def _get_response(self, request):
        response = get_response(server_wps_url, request)
        response_data = response.read()
        response_doc = etree.fromstring(response_data)

        return response_doc

    def test_sync(self):
        request = self._get_request(server_base_url + '/static/requests/buffer.xml')
        response = self._get_response(request)

        self.assertEqual(
            response.xpath(process_identifier,
                           namespaces=NAMESPACES)[0].text, 'buffer')

        self.assertEqual(
            response.xpath(
                process_succeeded,
                namespaces=NAMESPACES)[0].text,
            'PyWPS Process GDAL Buffer process finished')

        self.assertEqual(len(response.xpath(
            process_outputs,
            namespaces=NAMESPACES)), 1)

        self.assertEqual(response.xpath(
            process_outputs+'/wps:Data/wps:ComplexData',
            namespaces=NAMESPACES)[0].get('mimeType'),
                         'application/gml+xml')

        self.assertTrue(response.xpath(
            process_outputs+'/wps:Data/wps:ComplexData/ogr:FeatureCollection',
            namespaces=NAMESPACES))

    def test_async(self):
        request = self._get_request(server_base_url + '/static/requests/execute_buffer_async.xml')
        response = self._get_response(request)

        self.assertEqual(
            response.xpath(process_identifier,
                           namespaces=NAMESPACES)[0].text, 'buffer')

        self.assertTrue(response.xpath(
            process_accepted,
            namespaces=NAMESPACES))

        status_location = response.xpath(
            '//wps:ExecuteResponse',
            namespaces=NAMESPACES)[0].get('statusLocation')
        self.assertTrue(status_location)

        time.sleep(1)  # make sure, buffer is done
        status = self._get_request(status_location)
        status_doc = etree.fromstring(status)

        self.assertTrue(status_doc.xpath(
            process_succeeded,
            namespaces=NAMESPACES))

        self.assertTrue(status_doc.xpath(
            process_outputs+'/wps:Data/wps:ComplexData/ogr:FeatureCollection',
            namespaces=NAMESPACES))

    def test_async_reference(self):
        request = self._get_request(server_base_url + '/static/requests/execute_buffer_async_reference.xml')
        response = self._get_response(request)

        self.assertTrue(response.xpath(
            process_accepted,
            namespaces=NAMESPACES))

        status_location = response.xpath(
            '//wps:ExecuteResponse',
            namespaces=NAMESPACES)[0].get('statusLocation')
        self.assertTrue(status_location)

        time.sleep(1)  # make sure, buffer is done
        status = self._get_request(status_location)
        status_doc = etree.fromstring(status)

        self.assertTrue(status_doc.xpath(
            process_succeeded,
            namespaces=NAMESPACES))

        self.assertTrue(status_doc.xpath(
            process_outputs_reference,
            namespaces=NAMESPACES))

        self.assertEqual(status_doc.xpath(
            process_outputs_reference,
            namespaces=NAMESPACES)[0].get('mimeType'), 'application/gml+xml')

        data_href = status_doc.xpath(
            process_outputs_reference,
            namespaces=NAMESPACES)[0].get('{http://www.w3.org/1999/xlink}href')

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


if __name__ == "__main__":
    load_tests()
