
from pywps import Process, LiteralInput, LiteralOutput, UOM



class SayHello(Process):
    def __init__(self):
        process_id = 'say_hello'
        inputs = [LiteralInput('name', 'Input name', data_type='string', default='World')]
        outputs = [LiteralOutput('output', 'Output response', data_type='string')]

        super(SayHello, self).__init__(
            self._handler,
            identifier=process_id,
            title='Process Say Hello',
            abstract='Returns a literal string output\
             with Hello plus the inputed name',
            version='1.3.3.8',
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        response.outputs['output'].data = 'Hello ' + \
            request.inputs['name'][0].data
        response.outputs['output'].uom = UOM('unity')
        return response
