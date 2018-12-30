
import sys
sys.path.insert(0,'../..')

from demo import wps
from lxml import etree
from io import BytesIO
import re,os
import glob
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
import unittest
import tempfile
import shutil

class VariableTest(unittest.TestCase):

    def setUp(self):
        """Strategy for testing PYWPS_PROCESSES is to create a dummy process folder with only 1 process
         and test if the wps() function from demo.py picks up the variable path.
         For testing PYWPS_CFG we create a new pywps_testing.cfg that will sent a 'TESTING' string on the output"""
        
        self.tmp_dir = tempfile.mkdtemp()
        self.test_process = None
        self.pywps_cfg_name = "pywps_testing.cfg"
        self.testing_str = "TESTING"
        
        #remember unitests are called from top direcory
        with open("pywps.cfg",'r') as cfg_file:
            new_cfg_content = cfg_file.read().replace("PyWPS Demo server",self.testing_str)
            with open(os.path.join(self.tmp_dir,self.pywps_cfg_name),'w') as new_file:
                new_file.write(new_cfg_content)

        #make temporary dummy module        
        with open(os.path.join(self.tmp_dir,"__init__.py"), 'a'):
            os.utime(os.path.join(self.tmp_dir,"__init__.py"), None)

        glob.glob("./processes/*.py")
        process_list=glob.glob("./processes/*.py")
        try:
            process_list.remove("./processes/__init__.py")
        except:
            pass
        
        #no random process always the firs in list for consistency
        self.test_process = process_list[0]
        os.makedirs(os.path.join(self.tmp_dir,"processes"))
        shutil.copyfile(self.test_process,os.path.join(self.tmp_dir,"processes",os.path.basename(self.test_process)))


    def test_process_variable(self):
        """Test PYWPS_PROCESSES""" 

        os.environ["PYWPS_PROCESSES"]=os.path.join(self.tmp_dir,"processes")
        service = wps()
        c = Client(service, WPSBaseResponse)
        resp = c.get('?request=GetCapabilities&service=wps')
        
        process_return=resp.get_process_identifers()
        
        assert len(process_return) == 1   
        assert process_return[0][-1] in self.test_process
    
    def test_config_variable(self):
        """Test PYWPS_CFG"""
        os.environ["PYWPS_CFG"]= os.path.join(self.tmp_dir,self.pywps_cfg_name)
        service = wps()
        c = Client(service, WPSBaseResponse)
        resp = c.get('?request=GetCapabilities&service=wps')
        title= resp.get_title()
        assert title == self.testing_str
    
    def tearDown(self):
        """Removing temporary folder"""
        os.environ.pop("PYWPS_PROCESSES",None)
        os.environ.pop("PYWPS_CFG",None)
        shutil.rmtree(self.tmp_dir)
    
def load_tests(loader=None, tests=None, pattern=None):
    if not loader:
        loader = unittest.TestLoader()
    suite_list = [
        loader.loadTestsFromTestCase(VariableTest),
    ]
    return unittest.TestSuite(suite_list)




class WPSBaseResponse(BaseResponse):

    def __init__(self, *args):
        super(WPSBaseResponse, self).__init__(*args)
        if re.match(r'text/xml(;\s*charset=.*)?', self.headers.get('Content-Type')):
            #self.etree = etree.parse(BytesIO(self.get_data()))
            self.etree = etree.parse(BytesIO(self.get_data())).getroot()

            
    def get_title(self):
        # v1.0.0 and v2.0.0 have same path
        # Title is first child element after ServiceIdentification
        title_path = "//*[local-name() = 'ServiceIdentification']/*[1]"
        el_title = self.etree.xpath(title_path)
        if el_title:
            return el_title[0].text
        else:
            return None
    
    def get_process_identifers(self):
        identifier_path = "//*[local-name() = 'Identifier']"
        els_identifier=self.etree.xpath(identifier_path)
        if els_identifier:
            return [el.text for el in els_identifier]
        else:
            return None
        

