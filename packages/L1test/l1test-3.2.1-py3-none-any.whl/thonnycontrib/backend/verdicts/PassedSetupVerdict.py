from thonnycontrib.i18n.languages import tr
from .ExampleVerdict import ExampleVerdict

class PassedSetupVerdict(ExampleVerdict):
    def __init__(self, filename, lineno, tested_line):
        super().__init__(filename, lineno, tested_line, "None")

    def get_color(self):
        return "black"

    def isSuccess(self):
        return True
    
    def _verdict_message(self):
        return tr("Execution succeed")