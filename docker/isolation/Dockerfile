FROM alpine:3.6
MAINTAINER Jorge S. Mendes de Jesus <jorge.dejesus@geocat.net>

ARG GDAL_VERSION=2.3.2
ARG XERCES_VERSION=3.2.2
ARG PROCESSOR_N=4

RUN apk update && apk add --no-cache \
	git \
	gcc \
	bash \
	openssh \
	musl-dev  \
	python3 \
	python3-dev \
	libxml2-dev  \
	libxslt-dev \
	linux-headers \
	expat \
	expat-dev \
	g++ \
	libstdc++ \
	make \
	swig

RUN apk add --no-cache \
    --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
    geos \
    geos-dev

#Compiling Xerces
RUN wget http://www.apache.org/dist/xerces/c/3/sources/xerces-c-${XERCES_VERSION}.tar.gz -O /tmp/xerces-c-${XERCES_VERSION}.tar.gz && \
    tar xvf /tmp/xerces-c-${XERCES_VERSION}.tar.gz -C /tmp && \
    cd /tmp/xerces-c-${XERCES_VERSION} && \
    LDFLAGS="-s" ./configure --prefix=/usr/local/src/xerces && \
    make -j $PROCESSOR_N install

# Install GDAL
RUN wget http://download.osgeo.org/gdal/${GDAL_VERSION}/gdal-${GDAL_VERSION}.tar.gz -O /tmp/gdal.tar.gz && \
	tar xzf /tmp/gdal.tar.gz -C /tmp && \
	cd /tmp/gdal-${GDAL_VERSION} && \
	CFLAGS="-g -Wall" LDFLAGS="-s" ./configure --with-expat=yes --with-xerces=/opt/xerces --with-geos=yes \
	&& make -j $PROCESSOR_N && make install

RUN cd /tmp/gdal-${GDAL_VERSION}/swig/python \
	&& python3 setup.py build \
	&& python3 setup.py install

RUN rm -rf /var/cache/apk/*

RUN git clone https://github.com/lazaa32/pywps-flask.git

WORKDIR /pywps-flask
RUN pip3 install -r requirements.txt

EXPOSE 5000
ENTRYPOINT ["/usr/bin/python3", "demo.py","-a"]

#docker build -t pywps-flask .
#docker run -p 5000:5000 pywps-flask
#http://localhost:5000/wps?request=GetCapabilities&service=WPS
#http://localhost:5000/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0
