import re
from exceptions import BadUserInputError


def set_server(new_server_wps_url: str):
    pattern = r'((?:.*://)?(.*?)(?:(?::)(\d+))?(?:/.*?)?)$'
    m = re.match(pattern, new_server_wps_url)
    if not m:
        raise BadUserInputError('cannot parse server url: {}'.format(new_server_wps_url))
    # print(m.groups())
    server_wps_url = m.group(1)
    if server_wps_url.endswith('/'):
        server_wps_url = server_wps_url.rstrip('/')
    server_base_url = server_wps_url
    if server_base_url.endswith('/wps'):
        server_base_url = server_wps_url[:-4]
    else:
        server_wps_url = server_base_url + '/wps'
    server_hostname = m.group(2)
    server_port = m.group(3)
    if server_port:
        server_port = int(server_port)
    else:
        server_port = 80
    return server_hostname, server_port, server_base_url, server_wps_url, new_server_wps_url


if __name__ == '__main__':
    print(set_server('http://localhost:5000/abc/wps'))
    print(set_server('http://localhost:5000/wps'))
    print(set_server('http://localhost:5000/'))
    print(set_server('http://localhost:5000'))
    print(set_server('http://localhost/abc/wps'))
    print(set_server('http://localhost/wps'))
    print(set_server('http://localhost/'))
    print(set_server('localhost'))
    print(set_server('localhost:5000'))
    print(set_server('localhost:5000/'))
    print(set_server('localhost:5000/wps'))