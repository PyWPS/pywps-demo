#!/usr/bin/env python3

"""
This is example WSGI application of PyWPS, which can be used by e.g. Apache2
HTTPD server

Copyright (c) 2016 - PyWPS PSC

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""


import os
from pywps.app.Service import Service

from .processes import processes

def create_app(cfgfiles=None):
    config_files = [os.path.join(os.path.dirname(__file__), 'default.cfg')]
    print(config_files)
    if cfgfiles:
        config_files.extend(cfgfiles)
    if 'PYWPS_CFG' in os.environ:
        config_files.append(os.environ['PYWPS_CFG'])
    service = Service(processes=processes, cfgfiles=config_files)
    return service


application = create_app()


#from pywps.app.Service import Service

# processes need to be installed in PYTHON_PATH
#from processes.sleep import Sleep
#from processes.ultimate_question import UltimateQuestion
#from processes.centroids import Centroids
#from processes.sayhello import SayHello
#from processes.feature_count import FeatureCount
#from processes.buffer import Buffer
#from processes.area import Area


#processes = [
#    FeatureCount(),
#    SayHello(),
#    Centroids(),
#    UltimateQuestion(),
#    Sleep(),
#    Buffer(),
#    Area()
#]

#application = Service(processes, ['pywps.cfg'])
