import tempfile

from pywps import Process, LiteralInput, \
        ComplexInput, ComplexOutput, LiteralOutput, Format, FORMATS


from pywps.validator.mode import MODE

__author__ = 'Brauni'


class Buffer(Process):
    def __init__(self):
        inputs = [ComplexInput('poly_in', 'Input vector file',
                  supported_formats=[Format('application/gml+xml')],
                  mode=MODE.STRICT),
                  LiteralInput('buffer', 'Buffer size', data_type='float',
                  allowed_values=(0, 1, 10, (10, 10, 100), (100, 100, 1000)))]
        outputs = [ComplexOutput('buff_out', 'Buffered file',
                                 supported_formats=[
                                            Format('application/gml+xml')
                                            ]
                                 ),
                   LiteralOutput('r', 'input raster name', data_type='string')]

        super(Buffer, self).__init__(
            self._handler,
            identifier='buffer',
            version='0.1',
            title="GDAL Buffer process",
            abstract="""The process returns buffers around the input features,
             using the GDAL library""",
            profile='',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        from osgeo import ogr

        filename = request.inputs['poly_in'][0].file
        response.outputs['r'].data = filename
        in_source = ogr.Open(filename)

        in_layer = in_source.GetLayer()
        layer_name = in_layer.GetName() + '_buffer'
        out_filename = tempfile.mktemp()

        # create output file
        driver = ogr.GetDriverByName('GML')
        out_source = driver.CreateDataSource(
                                out_filename,
                                ["XSISCHEMAURI=\
                            http://schemas.opengis.net/gml/2.1.2/feature.xsd"])
        out_layer = out_source.CreateLayer(layer_name, None, ogr.wkbUnknown)

        # for each feature
        feature_count = in_layer.GetFeatureCount()
        index = 0

        while index < feature_count:
            # get the geometry
            in_feature = in_layer.GetNextFeature()
            in_geometry = in_feature.GetGeometryRef()

            # make the buffer
            buff = in_geometry.Buffer(float(request.inputs['buffer'][0].data))

            # create output feature to the file
            out_feature = ogr.Feature(feature_def=out_layer.GetLayerDefn())
            out_feature.SetGeometryDirectly(buff)
            out_layer.CreateFeature(out_feature)
            out_feature.Destroy()  # makes it crash when using debug
            index += 1

            response.update_status('Buffering', 100*(index/feature_count))

        out_source.Destroy()

        response.outputs['buff_out'].output_format = FORMATS.GML
        response.outputs['buff_out'].file = out_filename

        return response
