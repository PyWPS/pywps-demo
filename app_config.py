import pywps.configuration as config
from app_set_server import set_server
from set_root import set_root

set_root()

config_path = 'config/'
cfgfiles = [config_path + 'pywps.cfg']
config.load_configuration(cfgfiles)

# these defaults will be overwritten with the url from by the server\url from the config file
server_hostname = 'http://localhost'
server_port = 5000
server_base_url = '{}:{}'.format(server_hostname, server_port)
server_wps_url = server_base_url + '/wps'

server_hostname, server_port, server_base_url, server_wps_url, _ = set_server(config.get_config_value("server", "url"))
