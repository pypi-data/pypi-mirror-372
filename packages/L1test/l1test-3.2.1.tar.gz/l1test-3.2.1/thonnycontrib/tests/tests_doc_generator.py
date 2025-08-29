import unittest as ut
from thonnycontrib.frontend.docstring_generator.doc_generator import *
from unittest.mock import patch
from thonnycontrib.l1test_configuration import l1test_options

# last \n is added by doc_template.get_template 
DOCSTRING_PATTERN = '''""" ligne1

ligne3
"""'''

class MockDocGeneratorStrategy(DocGenerationStrategy):
    def __init__(self):
        super().__init__(text_widget=None)
        
    def can_generate(self) -> bool:
        pass
    
    def generate(self) -> None:
        pass

    def highlight_generated_docstring(self, doc_start_line, doc_end_line):
        pass

class TestDocGenerator(ut.TestCase):
    def setUp(self):
        self.docGenerationStrategy = MockDocGeneratorStrategy()
    
    def tearDown(self) -> None:
        del self.docGenerationStrategy
    
    @patch("thonnycontrib.frontend.docstring_generator.doc_template.get_option", return_value=DOCSTRING_PATTERN)
    def test_doc_generator_when_def_ok(self, mock_get_option):
        signature = "def func():"
        generated = self.docGenerationStrategy._generate(signature)
        expected = '''    """ ligne1

    ligne3
    """
'''
        self.assertEqual(expected, generated)

    @patch("thonnycontrib.frontend.docstring_generator.doc_template.get_option", return_value=DOCSTRING_PATTERN)
    def test_doc_generator_when_class_ok(self, mock_get_option):
        signature = "class Abj:"
        generated = self.docGenerationStrategy._generate(signature)
        expected = '''    """ ligne1

    ligne3
    """
'''
        self.assertEqual(expected, generated)
    
    # Ces tests ne sont plus pertinents pour la nouvelle version,
    # on ne génère plus la description des param + return
    # def test_doc_generator_typing_support_case_1(self):
    #     arg_type, r_type = "str", "int"
    #     signature = "def func(a: %s) -> %s:" % (arg_type, r_type)
    #     generated = self.docGenerationStrategy._generate(signature)
        
    #     self.assertTrue(len(generated) > 0)
    #     self.assertTrue(arg_type in generated)
    #     self.assertTrue(r_type in generated)
    
    # def test_doc_generator_typing_support_case_2(self):
    #     arg_type = "str"
    #     signature = "def func(a: %s):" % arg_type
    #     generated = self.docGenerationStrategy._generate(signature)
        
    #     self.assertTrue(len(generated) > 0)
    #     self.assertTrue(arg_type in generated)
    
    def test_doc_generator_when_syntax_error(self):
        signature = "def func):"
       
        with self.assertRaises(DocGeneratorParserException) as e:
            self.docGenerationStrategy._generate(signature)
        
        raised_exception = e.exception      
        self.assertTrue(SyntaxError.__name__ in str(raised_exception))
        
    def test_doc_generator_when_signature_doesnt_finish_with_colon(self):
        signature = "def func()"
        
        with self.assertRaises(NoFunctionSelectedToDocumentException) as e:
            self.docGenerationStrategy._generate(signature)


if __name__ == '__main__':
    ut.main(verbosity=2)   
