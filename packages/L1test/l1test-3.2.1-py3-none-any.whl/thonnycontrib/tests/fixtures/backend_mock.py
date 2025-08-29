from thonny.plugins.cpython_backend.cp_back import  MainCPythonBackend
from unittest.mock import *

class MockBackend(MainCPythonBackend):
    def __init__(self):
        pass
    
    def send_message(self, msg) -> None: pass

backend_patch = patch("thonnycontrib.backend.l1test_backend.BACKEND", 
                      return_value=MockBackend())