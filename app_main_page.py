import os
import sys
import flask
import pywps
import processes
import app_config

# This is, how you start PyWPS instance
service = pywps.Service(processes=processes.processes)
# config is read in app_config so we don't need to pass it to Service as well
# service = pywps.Service(processes=processes.processes, cfgfiles=cfgfiles)

main_page = flask.Blueprint('main_page', __name__, template_folder='templates')


@main_page.route('/test')
def test():
    return 'hello test!'


@main_page.route("/sys_path")
def sys_path():
    return str(sys.path)


# returns 'hello to the WPS server root'
@main_page.route('/wps', methods=['GET', 'POST'])
def wps():
    return service


@main_page.route("/")
def hello():
    request_url = flask.request.url
    return flask.render_template('home.html', request_url=request_url,
                                 server_url=app_config.server_wps_url,
                                 process_descriptor=processes.process_descriptor)


def flask_response(targetfile):
    if os.path.isfile(targetfile):
        with open(targetfile, mode='rb') as f:
            file_bytes = f.read()
        file_ext = os.path.splitext(targetfile)[1]
        mime_type = 'text/xml' if 'xml' in file_ext else None
        return flask.Response(file_bytes, content_type=mime_type)
    else:
        flask.abort(404)


@main_page.route('/outputs/' + '<path:filename>')
def outputfile(filename):
    targetfile = os.path.join('outputs', filename)
    return flask_response(targetfile)


@main_page.route('/data/' + '<path:filename>')
def datafile(filename):
    targetfile = os.path.join('static', 'data', filename)
    return flask_response(targetfile)


# not sure how the static route works. static route doesn't reach this function.
@main_page.route('/static/' + '<path:filename>')
def staticfile(filename):
    targetfile = os.path.join('static', filename)
    return flask_response(targetfile)
