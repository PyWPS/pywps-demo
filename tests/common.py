import lxml.etree as etree
import sys
import urllib

PY2 = sys.version_info[0] == 2

# server_wps_url, server_base_url are used in the tests
from app_config import server_wps_url, server_base_url

schema_wps_url = 'http://schemas.opengis.net/wps/1.0.0/wpsExecute_response.xsd'

NAMESPACES = {
    'xlink': "http://www.w3.org/1999/xlink",
    'wps': "http://www.opengis.net/wps/1.0.0",
    'ows': "http://www.opengis.net/ows/1.1",
    'gml': "http://www.opengis.net/gml",
    'xsi': "http://www.w3.org/2001/XMLSchema-instance",
    'ogr': "http://ogr.maptools.org/"
}

if not PY2:
    import urllib.request


def get_response(url, post_data=None):
    if PY2:
        response = urllib.urlopen(url, data=post_data)
    else:
        # if post_data:
        #    post_data = post_data.decode()
        response = urllib.request.urlopen(url, data=post_data)

    return response


def get_schema(url):
    if not hasattr(get_schema, "cache"):
        get_schema.cache = dict()
    if url not in get_schema.cache:
        schema_response = get_response(url)
        xmlschema_doc = etree.parse(schema_response)
        # etree.XMLSchema takes ages, so I cache the result
        get_schema.cache[url] = etree.XMLSchema(xmlschema_doc)
    return get_schema.cache[url]


def validate_file(path, schema):
    body_doc = etree.parse(path)
    schema = get_schema(schema)
    return schema.validate(body_doc)


def validate(url, schema, post_data=None):
    response = get_response(url, post_data)
    info = response.info()
    body = response.read()
    body_doc = etree.fromstring(body)

    schema = get_schema(schema)

    if schema.validate(body_doc):
        return True
    else:
        print(info)
        print(body)
        return False


if __name__ == '__main__':
    schema = get_schema(schema_wps_url)
    print(schema)
    schema = get_schema(schema_wps_url)
    print(schema)

