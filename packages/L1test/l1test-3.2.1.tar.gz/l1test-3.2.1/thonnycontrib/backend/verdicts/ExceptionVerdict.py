# Auteur : Esteban COLLARD, Nordine EL AMMARI
from thonnycontrib.i18n.languages import tr

from .ExampleVerdict import ExampleVerdict

class ExceptionVerdict(ExampleVerdict):
    def __init__(self, filename, lineno, tested_line, expected_result, error_details):
        super().__init__(filename, lineno, tested_line, expected_result, error_details)

    def get_color(self):
        return "red"

    def isSuccess(self):
        return False
    
    def _verdict_message(self):
        return tr("error")