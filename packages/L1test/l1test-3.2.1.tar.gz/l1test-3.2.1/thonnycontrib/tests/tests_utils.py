import unittest as ut
from thonnycontrib.utils import format_to_string

# Fichier créé pour tester format_to_string() que j'avais rajouté à utils.py.
# S'il existe déjà un fichier plus adéquat, ne pas hésiter à refactorer.

class TestUtils(ut.TestCase):
    def setup(self):
        pass
    
    def test_format_to_string(self):
        self.assertEqual( "42", format_to_string(42) )
        self.assertEqual( "'42'", format_to_string("42") )
        self.assertEqual( "''", format_to_string("") )