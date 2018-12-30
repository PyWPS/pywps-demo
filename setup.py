# Copyright (c) <year> <copyright holders>
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('VERSION.txt') as ff:
    VERSION = ff.read().strip()

with open('requirements.txt') as f:
    INSTALL_REQUIRES = f.read().splitlines()[:-1]
    INSTALL_REQUIRES.append('pywps=='+VERSION)

DESCRIPTION = (
    '''PyWPS is an implementation of the Web Processing Service standard from the
Open Geospatial Consortium. PyWPS is written in Python.

PyWPS-Flask is an example service using the PyWPS server, distributed along
with a basic set of sample processes and sample configuration file. It's
usually used for testing and development purposes.
    ''')

KEYWORDS = 'PyWPS WPS OGC processing'

config = {
    'description': DESCRIPTION,
    'keywords': KEYWORDS,
    'author': 'PyWPS PSC',
    'license': 'MIT',
    'platforms': 'all',
    'url': 'http://pywps.org',
    'download_url': 'https://github.com/lazaa32/pywps-flask',
    'author_email': 'luis.a.de.sousa@gmail.com',
    'maintainer': 'Luis de Sousa',
    'maintainer_email': 'luis.de.sousa@protonmail.ch',
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS'
    ],
    'version': VERSION,
    'install_requires': INSTALL_REQUIRES,
    'dependency_links': [
        'git+https://github.com/lazaa32/pywps.git@pywps-'
        + VERSION + '#egg=pywps-' + VERSION
     ],
    'packages': ['processes', 'tests'],
    'scripts': ['demo.py'],
    'name': 'pywps-flask'
}

setup(**config)
