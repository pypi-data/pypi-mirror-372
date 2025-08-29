# Auteur : Réda ID-TALEB
from thonnycontrib.i18n.languages import tr

from .FailedVerdict import FailedVerdict

class FailedWhenExceptionExpectedVerdict(FailedVerdict):
    def __init__(self, filename:str, lineno, tested_line, expected_result, failure_message=""):
        super().__init__(filename, lineno, tested_line, expected_result, failure_message)

    def isSuccess(self):
        return False
    
    def get_details(self):
        common = "%s %s `%s`" % (self.expected_result, tr("was not raised by"), self.tested_line)
        if self.details:
            common += "\n%s" % self.details
        return common

    def _verdict_message(self):
        return super()._verdict_message()