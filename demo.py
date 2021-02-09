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
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os

from app import app
from app_config import server_port

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
    parser.add_argument('-a', '--all-addresses',
                        action='store_true', help="run flask using IPv4 0.0.0.0 (all network interfaces)," +
                                                  "otherwise bind to 127.0.0.1 (localhost).  This maybe necessary in systems that only run Flask")
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
            print("%s [%d]" % (e.strerror, e.errno))

        if (pid == 0):
            os.setsid()
            app.run(threaded=True, host=bind_host, port=server_port)
        else:
            os._exit(0)
    else:
        app.run(threaded=True, host=bind_host, port=server_port)
