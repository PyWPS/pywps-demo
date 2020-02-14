============
Installation
============

The app depends on PyWPS and several other libraries that are listed in
``requirements.txt``. It is advisable to run it using a python virtualenv to prevent package installation problems::

    $ virtualenv -p python3 pywps_flask_env
    $ cd pywps_flask_dir
    $ . bin/activate
    $ git clone https://github.com/geopython/pywps-flask
    $ cd pywps-flask
    $ pip3 install -r requirements.txt

Alternatively you can also use a conda environment::

    $ conda create -n pywps-flask python=3.6 pip psutil
    $ conda activate pywps-flask
    $ git clone https://github.com/geopython/pywps-flask
    $ cd pywps-flask
    $ pip install -r requirements.txt

If python virtualenv or conda is not an option::

    $ git clone https://github.com/geopython/pywps-flask
    $ cd pywps-flask
    $ pip3 install -r requirements.txt



For Debian based systems you will need to install GDAL with::

    $ sudo apt-get install python3-gdal


When using only using `requirement.txt`, the `pywps-flask` will run for the directory that was pulled from github, for a system wise installation is it advisable to use `setup.py`::

    $ git clone https://github.com/geopython/pywps-flask
    $ cd pywps-flask
    $ python3 setup.py install


=======
Running
=======

Simply run the python file::

    $ python3 demo.py -a

The flag `-a` will bind to the ip range `0.0.0.0` and is normally the safest option access to `pypwps-flask`

The `-d`  option will run pywps-flask as daemon and to stop it is necessary to determine the PID and kill it, one trick is to use fuser to determine PID, and then use it to kill the process::

    $ fuser tcp/5000
    $ kill -15 <PID RETURNED PREVIOUSLY>



==============
Docker  images
==============

The docker folder contains 2 subfolders, each subfolder contains a differente pywps implementation.

Folder ``flask``  has the default pywps-flask implementation using only Flask while folder ``nginx``  implements pywps using Nginx and Green unicorn as WSGI server. While folder ``ubuntu`` has the same images but using phusion image (ubuntu 18.04)



Flask-Alpine (basic)
--------------------

Basic pywps image is based on Alpine 3.8 and will run the native Flask service, this is not apropriate for production. The docker file can be found in: ``docker/alpine/flask/Dockerfile``



To build the image (inside the folder with the Dockerfile)::

    $ docker build -t pywps/flask-alpine .

And to run it::

    $ docker run -p 5000:5000 pywps/flask-alpine:latest


Pywps will be available in  the following URL::

    $ http://localhost:5000



Gunicorn-Alpine (production)
----------------------------

This image implements the previous ``flask-alpine image`` (you need to build it first, or it will be automatically pulled from dockerhub) but wrapping flask in a WSGI server (gunicorn) where each worker runs a an app. This image allows for the following environment variables:

 - GU_WORKERS - Numer or workers. Gunicorn uses a set of workers to run pywps (normally ``workers = (2 * cpu) + 1``).  (default: 5)
 - GU_PORT  - Port running Gunicorn (default:8081)



Gunicorn-Alpine is locate in folder ``docker/alpine/gunicorn/Dockerfile``

This image can already be implemented in production but it is advisable to use Nginx for HTTP load balance and Gunicorn as WSGI server (see below)

To build the image (inside the folder with the Dockerfile)::

    $ docker build -t pywps/gunicorn-alpine:latest .


And to run it::

    $ docker run -p 8081:8081 -it pywps/gunicorn-alpine:latest

or::

    $ docker run -e GU_WORKERS=10 -e GU_PORT=8082  -p 8082:8082 -it pywps/gunicorn-alpine:latest

Pywps will be available at the following URL::

    $ http://localhost:8082


Nginx-Alpine
------------

This is the complete stack intented for production, to have a stack we require to use ``docker-compose``
to build two images: ``pywps/gunicorn-alpine:latest``  and ``pywps/nginx-alpine:latest``

Those images will be pulled from dockerhub, but they can compiled locally by building Flask-Alpine, Gunicron-Alpine and Nginx-Alpine, in this case only showing for nginx::


   $ cd docker/alpine/nginx/Dockerfile
   $ docker build -t pywps/nginx-alpine:latest .

Then the stack can be started using docker compose::

   $ docker-compose up


In this case pywps (only the WPS) will be avalable on::


    http://localhost


Flask-Ubuntu (basic)
--------------------

The same as ``Flask-Ubuntu`` but using phusion image (ubuntu 18.04)::


    $ cd docker/ubuntu/flask
    $ docker build -t pywps/flask-ubuntu:latest .

And to run it::

    $ docker run -p 5000:5000 pywps/flask-ubuntu


Nginx-Ubuntu (production)
-------------------------

This image is based on ``Flask-Ubuntu`` and will require it (either build locally or pull from dockerhub). This image has Nginx and Gunicorn totally integrated as services in a docker image::


   $ cd docker/ubuntu/nginx
   $ docker build -t pywps/nginx-ubuntu .

And to run it::

   $ docker run -p 80:80 pywps/nginx-ubuntu

It is possible to set the number of Gunicorn workers:

* GU_WORKERS - Numer or workers.  (default: 5)

e.g::

   $ docker run -e GU_WORKERS=10 -p 80:80 pywps/nginx-ubuntu



Volumes
-------


Named volumes allow for container content to be available in the host system. The most important folders in pywps containers are:

* /pywps-flask/logs
* /pywps-flask/outputs
* /pywps-flask/processes

And file:
* /pywps-flask/pywps.cfg

Named volumes need to be created prior to ``docker run``::

    $ docker volume create pywps_logs
    $ docker volume create pywps_outputs
    $ docker volume create pywps_processes

To check the path on the host to volume and other information::


   $ docker volume ls pywps_processes


To run a docker will all the volumes available in the host::

  $ docker run -p 5000:5000 -v pywps_logs:/pywps-flask/pywps_logs \
                            -v pywps_outputs:/pywps-flask/pywps_outputs \
                            -v pywps_processes:/pywps-flask/pywps_processes \
                            -v pywps_cfg:/pywps-flask/pywps.cfg  pywps/flask-alpine:latest


THE END
=======
