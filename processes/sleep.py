# Copyright (c) 2016 PyWPS Project Steering Committee
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

from pywps import Process, LiteralInput, LiteralOutput
from pywps.app.Common import Metadata


class Sleep(Process):
    
    SUCCESS_MESSAGE = 'done sleeping'
    
    def __init__(self):
        inputs = [LiteralInput('delay', 'Delay between every update', data_type='float', default=10),
                  LiteralInput('times', 'Update times', data_type='positiveInteger', default=5)]
        outputs = [LiteralOutput('sleep_output', self.SUCCESS_MESSAGE+' Output', data_type='string'),
                   LiteralOutput('time', 'Float Output response', data_type='float'),
                   LiteralOutput('output', 'String Output response', data_type='string')]

        super(Sleep, self).__init__(
            self._handler,
            identifier='sleep',
            version='None',
            title='Sleep Process',
            abstract="The process will sleep for a given delay \
            or 10 seconds if not a valid value",
            profile='',
            metadata=[Metadata('Sleep'), Metadata('Wait'), Metadata('Delay')],
            inputs=inputs,
            outputs=outputs,
            store_supported=True,
            status_supported=True
        )

    def _handler(self, request, response):
        import time

        t = time.time()
        sleep_delay = float(request.inputs['delay'][0].data)
        sleep_times = int(request.inputs['times'][0].data)

        for i in range(sleep_times):
            response.update_status('PyWPS Process started. Waiting...', 100*i/sleep_times)
            time.sleep(sleep_delay)
        t = time.time() - t

        response.outputs['sleep_output'].data = self.SUCCESS_MESSAGE
        response.outputs['time'].data = t
        response.outputs['output'].data = 'I slept for {} sleep_delay'.format(t)

        return response
    
    
def main():
    """Example of how to debug this process, running outside a PyWPS instance.
    """
    sleep = Sleep()
    (request, response) = sleep.build_request_response()
    literal_in = sleep.inputs[0]
    literal_in.data = 10
    request.inputs["delay"].append(literal_in)
    sleep._handler(request, response)

    assert response.outputs["sleep_output"].data == sleep.SUCCESS_MESSAGE
    print("All good!") 


if __name__ == "__main__":
    main()
