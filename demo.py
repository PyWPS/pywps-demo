#!/usr/bin/env python
import flask
import multiprocessing
import os
import psutil
import sys
from flask import request
import shutil
from werkzeug.wrappers import Response

# CAUTION! This line is only used for a development environment, when pywps is not installed
sys.path.append(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    os.path.pardir))

from server import Server
from processes.sleep import Sleep
from processes.ultimate_question import UltimateQuestion
from processes.centroids import Centroids
from processes.sayhello import SayHello
from processes.feature_count import FeatureCount
from processes.buffer import Buffer
from processes.area import Area
from processes.bboxinout import Box


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-w', '--waitress', action='store_true')
    parser.add_argument('-d', '--daemon', action='store_true')
    args = parser.parse_args()

    if args.daemon:
        pid = None
        try:
            pid = os.fork()
        except OSError as e:
             raise Exception("%s [%d]" % (e.strerror, e.errno))

        if (pid == 0):
            os.setsid()
            start(args)
        else:
            os._exit(0)

    else:
        start(args)

def start(args, kill = None):

    from pywps import configuration
    # TODO: the config file should be "global" to a single server instance and not across all
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pywps.cfg")
    configuration.load_configuration(config_file)
    rest_url = '/wpsadmin'


    processes = [
        FeatureCount(),
        SayHello(),
        Centroids(),
        UltimateQuestion(),
        Sleep(),
        Buffer(),
        Area(),
        Box()
    ]

    # List of servers to start up
    server_list = [
        Server(processes=processes, host='0.0.0.0', port=5001, config_files=[config_file]),
        Server(processes=processes, host='0.0.0.0', port=5002)
    ]

    # List of server instances running
    server_instances = {}
    for s in server_list:
        p = multiprocessing.Process(target=s.run)
        p.start()
        server_instances[p.pid] = {'Process': p, 'ServerObject': s}

    if args.waitress:
        # TODO: make waitress use multiprocessing
        pass
        import waitress

        host = configuration.get_config_value('wps', 'serveraddress').split('://')[1]
        port = int(configuration.get_config_value('wps', 'serverport'))

        waitress.serve(s.app, host=host, port=port)
    else:
        rest_app = flask.Flask(__name__)

        # REST INDEX
        @rest_app.route('/', strict_slashes=False)
        @rest_app.route(rest_url, strict_slashes=False)
        def rest_index():
            rest_url_config = flask.url_for('rest_configuration', _external=True)
            rest_url_config_id = flask.url_for('rest_configuration_id', server_id=0, _external=True)
            rest_url_server = flask.url_for('rest_server', _external=True)
            rest_url_server_id = flask.url_for('rest_server_id', server_id=0, _external=True)
            rest_url_server_pause = flask.url_for('rest_server_pause', server_id=0, _external=True)
            rest_url_server_resume = flask.url_for('rest_server_resume', server_id=0, _external=True)
            rest_url_server_processes = flask.url_for('rest_server_processes', server_id=0, _external=True)
            rest_url_server_process_id = flask.url_for('rest_server_process_id', server_id=0, process_id=1, _external=True)
            rest_url_server_process_name = flask.url_for('rest_server_process_name', server_id=0, process_name='1', _external=True)
            rest_url_pywps_processes = flask.url_for('rest_pywps_processes', _external=True)
            rest_url_pywps_process = flask.url_for('rest_pywps_process', process_name='0', _external=True)

            rest_url_config_id = rest_url_config_id.replace('/0', '/<int:server_id>')
            rest_url_server_id = rest_url_server_id.replace('/0', '/<int:server_id>')
            rest_url_server_pause = rest_url_server_pause.replace('/0', '/<int:server_id>')
            rest_url_server_resume = rest_url_server_resume.replace('/0', '/<int:server_id>')
            rest_url_server_processes = rest_url_server_processes.replace('/0', '/<int:process_id>')
            rest_url_server_process_id = rest_url_server_process_id.replace('/0', '/<int:server_id>')
            rest_url_server_process_id = rest_url_server_process_id.replace('/1', '/<int:process_id>')
            rest_url_server_process_name = rest_url_server_process_name.replace('/0', '/<int:server_id>')
            rest_url_server_process_name = rest_url_server_process_name.replace('/1', '/<string:process_name>')
            rest_url_pywps_process = rest_url_pywps_process.replace('/0', '/<string:process_name>')

            return flask.render_template('rest.html',
                                         rest_url_config=rest_url_config,
                                         rest_url_config_id=rest_url_config_id,
                                         rest_url_server=rest_url_server,
                                         rest_url_server_id=rest_url_server_id,
                                         rest_url_server_pause=rest_url_server_pause,
                                         rest_url_server_resume=rest_url_server_resume,
                                         rest_url_server_processes=rest_url_server_processes,
                                         rest_url_server_process_id=rest_url_server_process_id,
                                         rest_url_server_process_name=rest_url_server_process_name,
                                         rest_url_pywps_processes=rest_url_pywps_processes,
                                         rest_url_pywps_process=rest_url_pywps_process
                                         )

        # REST get all server configuration
        @rest_app.route(rest_url+'/configuration', methods=['GET'], strict_slashes=False)
        def rest_configuration():
            js = {}
            for s in server_instances:
                process = server_instances[s]['Process']
                server = server_instances[s]['ServerObject']
                json_server = {}
                config = server.get_configuration()
                for section in config.sections():
                    for (key, val) in config.items(section):
                        json_server[key] = val
                js[process.pid] = json_server
            response = flask.jsonify(js)
            response.status_code = 200
            return response

        # REST specific server configuration
        @rest_app.route(rest_url+'/configuration/<int:server_id>', methods=['GET', 'PUT'], strict_slashes=False)
        def rest_configuration_id(server_id):
            if request.method == 'GET':
                try:
                    process = server_instances[server_id]['Process']
                    server = server_instances[server_id]['ServerObject']
                    json_server = {}
                    config = server.get_configuration()
                    for section in config.sections():
                        for (key, val) in config.items(section):
                            json_server[key] = val
                    response = flask.jsonify(json_server)
                    response.status_code = 200
                    return response
                except:
                    return Response(status=500)
            elif request.method == 'PUT':
                try:
                    # only parse json and if Header Content-Type is application/json
                    data = request.get_json()

                    #  TODO: check if configuration key is valid

                    server = server_instances[server_id]['ServerObject']
                    config = server.get_configuration()

                    for section in config.sections():
                        for (key, val) in config.items(section):
                            if key in data:
                                config.set(section, key, data[key])

                    # remove running instance so we can create an updated version
                    if server_id in server_instances:
                        _terminate_process(server_id)

                    # create and add process
                    server_put = Server(processes=processes)
                    server_put.set_configuration(config)
                    process_put = multiprocessing.Process(target=server_put.run)
                    process_put.start()
                    server_instances[server_id] = {'Process': process_put, 'ServerObject': server_put}
                    return Response(status=201)
                except:
                    return Response(status=500)

        # REST get all server information
        @rest_app.route(rest_url+'/server', methods=['GET'], strict_slashes=False)
        def rest_server():
            js = {}
            for s in server_instances:
                process = server_instances[s]['Process']
                server = server_instances[s]['ServerObject']

                p = psutil.Process(process.pid)

                json_server = {}
                json_server['pid'] = process.pid
                json_server['host'] = server.host
                json_server['port'] = server.port
                json_server['status'] = p.status
                js[s] = json_server
            response = flask.jsonify(js)
            response.status_code = 200
            return response

        # REST specific server information
        @rest_app.route(rest_url+'/server/<int:server_id>', methods=['GET', 'PUT', 'DELETE'], strict_slashes=False)
        def rest_server_id(server_id):
            if request.method == 'GET':
                try:
                    process = server_instances[server_id]['Process']
                    server = server_instances[server_id]['ServerObject']

                    p = psutil.Process(server_id)

                    json_server = {}
                    json_server['pid'] = process.pid
                    json_server['host'] = server.host
                    json_server['port'] = server.port
                    json_server['status'] = p.status
                    response = flask.jsonify(json_server)
                    response.status_code = 200
                    return response
                except:
                    return Response(status=500)

            if request.method == 'PUT':
                try:
                    # only parse json and if Header Content-Type is application/json
                    data = request.get_json()

                    if 'host' not in data:
                        return Response(response='No host specified!', status=400)

                    if 'port' not in data:
                        return Response(response='No port specified!', status=400)

                    # remove running instance so we can create an updated version
                    if server_id in server_instances:
                        _terminate_process(server_id)

                    # create and add process
                    server_put = Server(processes=processes, host=data['host'], port=data['port'])
                    process_put = multiprocessing.Process(target=server_put.run)
                    process_put.start()
                    server_instances[server_id] = {'Process': process_put, 'ServerObject': server_put}
                    return Response(status=201)
                except:
                    return Response(status=500)

            if request.method == 'DELETE':
                try:
                    if server_id in server_instances:
                        _terminate_process()
                    return Response(status=200)
                except Exception as e:
                    return Response(status=500)

            return Response(status=405)

        # REST pause a specific server
        @rest_app.route(rest_url+'/server/<int:server_id>/pause', methods=['GET'], strict_slashes=False)
        def rest_server_pause(server_id):
            if request.method == 'GET':
                try:
                    p = psutil.Process(server_id)

                    if p.status == psutil.STATUS_RUNNING or p.status == psutil.STATUS_SLEEPING:
                        p.suspend()
                        return Response('Suspended running Server with PID %s' % server_id, status=200)
                    else:
                        return Response('Server with PID %s already suspended' % server_id, status=200)
                except:
                    return Response(status=500)

        # REST resume a specific server
        @rest_app.route(rest_url+'/server/<int:server_id>/resume', methods=['GET'], strict_slashes=False)
        def rest_server_resume(server_id):
            if request.method == 'GET':
                try:
                    p = psutil.Process(server_id)

                    if p.status == psutil.STATUS_STOPPED:
                        p.resume()
                        return Response('Resumed suspended Server with PID %s' % server_id, status=200)
                    else:
                        return Response('Server with PID %s already resumed' % server_id, status=200)
                except:
                    return Response(status=500)

        # REST get and delete pywps processes of a specific server
        @rest_app.route(rest_url+'/server/<int:server_id>/process', methods=['GET', 'DELETE'], strict_slashes=False)
        def rest_server_processes(server_id):
            if request.method == 'GET':
                # TODO: Get list of all the processes activated on the specified server
                return Response(status=501)
            elif request.method == 'DELETE':
                # TODO: Deactivate/Remove all the processes from the specified server
                return Response(status=501)

        # REST activate and deactivate a specific process of a specific server with the process ID
        @rest_app.route(rest_url+'/server/<int:server_id>/process/id/<int:process_id>', methods=['DELETE'], strict_slashes=False)
        def rest_server_process_id(server_id, process_id):
            if request.method == 'PUT' or request.method == 'POST':
                # TODO: Activate the specified process for the specified server
                return Response(status=501)
            elif request.method == 'DELETE':
                # TODO: Deactivate/Remove the specified server process
                return Response(status=501)

        # REST activate or deactivate a specific process of a specific server with the process name
        @rest_app.route(rest_url+'/server/<int:server_id>/process/name/<process_name>', methods=['PUT', 'POST', 'DELETE'], strict_slashes=False)
        def rest_server_process_name(server_id, process_name):
            if request.method == 'PUT' or request.method == 'POST':
                # TODO: Activate the specified process for the specified server
                return Response(status=501)
            elif request.method == 'DELETE':
                # TODO: Deactivate/Remove the specified server process
                return Response(status=501)

        # REST get all the pywps processes available inside the process folder and delete all available processes completely
        @rest_app.route(rest_url+'/server/process', methods=['GET', 'DELETE'], strict_slashes=False)
        def rest_pywps_processes():
            if request.method == 'GET':
                try:
                    json_server = {}
                    json_server['processes'] = {}

                    process_dir = os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processes'))

                    i = 0
                    for f in process_dir:
                        if f.endswith('.py') and f.lower() != '__init__.py':
                            json_server['processes'][i] = f
                            i += 1
                    response = flask.jsonify(json_server)
                    response.status_code = 200
                    return response
                except:
                    return Response(status=500)
            elif request.method == 'DELETE':
                try:
                    process_dir = os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processes'))

                    for f in process_dir:
                        if os.path.exists(f):
                            os.remove(f)
                    return Response(status=200)
                except:
                    return Response(status=500)

        # REST get, add, update and delete a pywps process specified by its file name
        @rest_app.route(rest_url+'/server/process/<string:process_name>', methods=['GET', 'PUT', 'POST', 'DELETE'], strict_slashes=False)
        def rest_pywps_process(process_name):
            if request.method == 'GET':
                try:
                    process_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processes')
                    process_file = os.path.join(process_dir, process_name)
                    with open(process_file, 'r') as f:
                        data = f.read()

                    return Response(data, status=200)
                except:
                    return Response(status=500)
            elif request.method == 'PUT':
                try:
                    data = request.data
                    process_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processes')
                    process_file = os.path.join(process_dir, process_name)
                    if os.path.exists(process_file):
                        with open(process_file, 'w') as f:
                            f.write(data)
                    else:
                        return Response('No such process: %s' % process_name, status=500)

                    return Response(status=201)
                except:
                    return Response(status=500)
            elif request.method == 'POST':
                try:
                    data = request.data
                    process_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processes')
                    process_file = os.path.join(process_dir, process_name)
                    with open(process_file, 'w') as f:
                        f.write(data)

                    return Response(status=201)
                except:
                    return Response(status=500)
            elif request.method == 'DELETE':
                try:
                    process_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processes')
                    process_file = os.path.join(process_dir, process_name)

                    if os.path.exists(process_file):
                        os.remove(process_file)
                    return Response(status=200)
                except:
                    return Response(status=500)

        # Terminates a process and removes it from the list
        def _terminate_process(server_id):
            process_delete = server_instances[server_id]['Process']
            process_delete.terminate()
            process_delete.join()
            if process_delete.is_alive():
                return Response(response='Error terminating process: %s with pid: %s' % (server_id, process_delete.pid), status=500)
            del server_instances[server_id]

        rest_app.run(host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
