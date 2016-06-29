import os
import flask
from pywps import Service
from pywps.exceptions import NoApplicableCode
from pywps.wpsserver import PyWPSServerAbstract
from pywps import configuration


class Server(PyWPSServerAbstract):
    def __init__(self, host=None, port=None, debug=False, processes=[],
            config_files=None):

        self.app = flask.Flask(__name__)

        # Load config files and override settings if any file specified
        if config_files:
            configuration.load_configuration(config_files)
            self.host = configuration.get_config_value('server', 'url').split('://')[1]
            self.port = configuration.get_config_value('server', 'port')
            if self.port:
                self.port = int(self.port)

        # Override config host and port if they are passed to the constructor
        if host:
            self.host = host
        if port:
            self.port = port
        self.debug = debug

        self.output_url = configuration.get_config_value('server', 'outputurl')
        self.output_path = configuration.get_config_value('server', 'outputpath')
        self.temp_path = configuration.get_config_value('server', 'workdir')

        # check if in the configuration file specified directory exists otherwise create it
        try:
            if not os.path.exists(self.temp_path):
                os.makedirs(self.temp_path)
                print('%s does not exist. Creating it.' % self.temp_path)
            if not os.path.exists(self.output_path):
                os.makedirs(self.output_path)
                print('%s does not exist. Creating it.' % self.output_path)
        except Exception as e:
            raise NoApplicableCode('File error: Could not create folder. %s' % e)

        self.processes = processes
        self.service = Service(processes=self.processes, cfgfiles=config_files)

    def run(self):
        @self.app.route('/')
        def index():
            url = flask.url_for('wps', _external=True)
            return flask.render_template('home.html', url=url)

        @self.app.route('/wps', methods=['GET', 'POST'])
        def wps():
            return self.service

        @self.app.route(self.output_url+'<uuid>')
        def datafile(uuid):
            for data_file in os.listdir(self.output_path):
                if data_file == uuid:
                    file_ext = os.path.splitext(data_file)[1]
                    with open(os.path.join(self.output_path, data_file), mode='rb') as f:
                        file_bytes = f.read()
                    mime_type = None
                    if 'xml' in file_ext:
                        mime_type = 'text/xml'
                    return flask.Response(file_bytes, content_type=mime_type)
            else:
                flask.abort(404)

        self.app.run(host=self.host, port=self.port, debug=self.debug)

    def shut_down(self):
        func = request.environ.get('werkzeug.server.shutdown')
        func()
