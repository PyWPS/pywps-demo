import os
from osgeo import ogr
from pywps import Process, ComplexInput, LiteralOutput, Format
from pywps.wpsserver import temp_dir

import logging
LOGGER = logging.getLogger('PYWPS')
LOGGER.info('Adquired logger inside total_length.py')

class TotalLength(Process):
    """Process calculating area of given polygon
    """
    def __init__(self):
        inputs = [ComplexInput('layer', 'Layer',
                               [Format('application/gml+xml')])]
        outputs = [LiteralOutput('total', 'Total', data_type='string')]

        super(TotalLength, self).__init__(
            self._handler,
            identifier='total_length',
            title='Process Total Length',
            abstract="""Process returns the total length of all lines in a submitted GML file""",
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        with temp_dir() as tmp:
        
            input_gml = request.inputs['layer'][0].file
            
            driver = ogr.GetDriverByName("GML")
            
            dataSource = driver.Open(input_gml, 0)
            layer = dataSource.GetLayer()
            total = 0
            
            LOGGER.info('Hola!! y que tal ???')
            
            for feature in layer:
                total = total + feature.length
            response.outputs['total'].data = str(total)
            return response
