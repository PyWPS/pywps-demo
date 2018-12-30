#!/usr/bin/env python3

# Copyright (c) 2016 PyWPS Project Steering Committee
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission
# notice shall be included in all copies
# or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import glob
import inspect
import importlib
import flask
import pywps
from pywps import Service

# dynamically loading processes,
# using PYWPS_PROCESSES if not the load default processes on folder processes

def get_processes():
 
    PYWPS_PROCESSES = os.environ["PYWPS_PROCESSES"] if "PYWPS_PROCESSES" in os.environ else "./processes"
    package_processes = os.path.basename(os.path.abspath(PYWPS_PROCESSES))
    modules = glob.glob(os.path.abspath(PYWPS_PROCESSES)+"/*.py")
    # need relative modules with (.)
    modules = ["." + os.path.basename(f)[:-3]
               for f in modules if os.path.isfile(f)
               and not f.endswith('__init__.py')]
     
    processes = []
    for module_name in modules:
        module = importlib.import_module(module_name, package_processes)
        # getting all member is module and
        # then fiter for classes and pywps processes
        process_classes = inspect.\
            getmembers(module, lambda member: inspect.isclass(member)
                       and member.__module__ == module.__name__)
        for process_class in process_classes:
            # [('Sleep', <class 'processes.sleep.Sleep'>)]
            processes.append(getattr(module, process_class[0]).__call__())
    
    
   # For the process dict on the home page
    return processes 


app = flask.Flask(__name__)

@app.route("/")
def hello():
    
    process_descriptor = {}
    
    for process in get_processes():
        abstract = process.abstract
        identifier = process.identifier
        process_descriptor[identifier] = abstract
    
    server_url = pywps.configuration.get_config_value("server", "url")
    request_url = flask.request.url
    return flask.render_template('home.html', request_url=request_url,
                                 server_url=server_url,
                                 process_descriptor=process_descriptor)


@app.route('/wps', methods=['GET', 'POST'])
def wps():
    # Need to determine config files
    def create_wps_app():
        config_files = [os.path.join(os.path.dirname(__file__), 'pywps.cfg')]
        if 'PYWPS_CFG' in os.environ:
            config_files.append(os.environ['PYWPS_CFG'])
        service = Service(processes=get_processes(), cfgfiles=config_files)
        return service

    return create_wps_app()


@app.route('/outputs/'+'<path:filename>')
def outputfile(filename):
    targetfile = os.path.join('outputs', filename)
    if os.path.isfile(targetfile):
        file_ext = os.path.splitext(targetfile)[1]
        with open(targetfile, mode='rb') as f:
            file_bytes = f.read()
        mime_type = None
        if 'xml' in file_ext:
            mime_type = 'text/xml'
        return flask.Response(file_bytes, content_type=mime_type)
    else:
        flask.abort(404)


@app.route('/static/'+'<path:filename>')
def staticfile(filename):
    targetfile = os.path.join('static', filename)
    if os.path.isfile(targetfile):
        with open(targetfile, mode='rb') as f:
            file_bytes = f.read()
        mime_type = None
        return flask.Response(file_bytes, content_type=mime_type)
    else:
        flask.abort(404)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description="""Script for starting an example PyWPS
                       instance with sample processes""",
        epilog="""Do not use this service in a production environment.
         It's intended to be running in test environment only!
        For more documentation, visit http://pywps.org/doc
        """
        )
    parser.add_argument('-d', '--daemon',
                        action='store_true', help="run in daemon mode")
    parser.add_argument('-a', '--all-addresses', action='store_true',
                        help="run flask using IPv4 0.0.0.0 "
                        + "(all network interfaces),"
                        + "otherwise bind to 127.0.0.1 (localhost)."
                        + "This maybe necessary in"
                        + "systems that only run Flask")
    args = parser.parse_args()

    if args.all_addresses:
        bind_host = '0.0.0.0'
    else:
        bind_host = '127.0.0.1'

    if args.daemon:
        pid = None
        try:
            pid = os.fork()
        except OSError as e:
            raise Exception("%s [%d]" % (e.strerror, e.errno))

        if (pid == 0):
            os.setsid()
            app.run(threaded=True, host=bind_host)
        else:
            os._exit(0)
    else:
        app.run(threaded=True, host=bind_host)
