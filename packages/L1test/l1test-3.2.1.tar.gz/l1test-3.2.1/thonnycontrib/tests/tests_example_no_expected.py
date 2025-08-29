from types import ModuleType
import unittest as ut
from thonnycontrib.tests.fixtures.backend_mock import *
from thonnycontrib.backend.doctest_parser import ExampleWithoutExpected
from unittest.mock import *
from thonnycontrib.backend.evaluator import Evaluator
from thonnycontrib.exceptions import *
from thonnycontrib.backend.verdicts.PassedSetupVerdict import PassedSetupVerdict
from thonnycontrib.backend.ast_parser import *
from thonnycontrib.backend.verdicts.ExceptionVerdict import ExceptionVerdict
from thonnycontrib.backend.doctest_parser import *

# #######################################################
#    Tous les tests qui suivent utilisent l'invite `$$$`
#               SANS valeur attendue  
# #######################################################
class TestEvaluator(ut.TestCase):
    def setUp(self):
        self.evaluator = Evaluator(filename="<string>")
        self.mock_backend = backend_patch.start()
    
    def tearDown(self) -> None:
        del self.evaluator
        backend_patch.stop()
    
    """
    Ce test vérifie:
    1. Le type `ExampleWithoutExpected` est le type `Example` extrait 
    par le doctest parser.
    2. S'il existe que des setups réussi dans une fonction alors le l1doctest associé aura 
    le flag EMPTY_FLAG. On assure aussi que le verdict associé à l'example est PassedSetupVerdict
    """
    def test_evaluate_when_setup(self):
        fake_source = \
"""
def f(a, b):
    '''
    $$$ a = 0
    '''
    if a < 0 and b < 0:
        return None
    return a + b
""" 
        
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # ###########################################################
        # ------------- Vérification du type Example ----------------
        self._assert_example_type(ExampleWithoutExpected) # assure qu'il y a un seul example
        
        # ###################################################
        # ------------- Vérification du verdict -------------
        l1doctests = self.evaluator.evaluate()
    
        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1)
        l1doctest = l1doctests[0]
        
        # on assure que l1doctest ne contient aucun tests
        self.assertTrue(l1doctest.has_only_setUps())
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.EMPTY_FLAG)
        
        # on assure que le verdict de l'example est un setUp qui réussit
        examples = l1doctest.get_examples()
        self.assertTrue(len(examples) == 1) # on assure qu'il existe un seul type Example
        self.assertTrue(isinstance(l1doctest.get_verdict_from_example(examples[0]), PassedSetupVerdict))   
    
    """
    Ce test vérifie:
    1. Le type `ExampleWithoutExpected` est le type `Example` extrait 
    par le doctest parser.
    2. S'il existe une erreur de syntaxe au niveau du setup alors
    un verdict `ExceptionTest` sera renvoyé. Le flag associé au l1doctest sera alors FAILED_FLAG
    """
    def test_evaluate_when_syntax_error_on_setup(self):  
        fake_source = \
"""
def f(a, b):
    '''
    $$$ a = 
    '''
    if a < 0 and b < 0:
        return None
    return a + b
""" 
        
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # ###########################################################
        # ------------- Vérification du type Example ----------------
        self._assert_example_type(ExampleWithoutExpected)
        
        # ###################################################
        # ------------- Vérification du verdict -------------
        l1doctests = self.evaluator.evaluate()

        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1)
        l1doctest = l1doctests[0]
        
        # on assure que l1doctest contient aucun test, mais qu'il exisite une erreur
        self.assertTrue(l1doctest.has_only_setUps())
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.FAILED_FLAG)
        
        # on assure que le verdict de l'example est en erreur
        examples = l1doctest.get_examples()
        self.assertTrue(len(examples) == 1) # on assure qu'il existe un seul type Example
        
        verdict = l1doctest.get_verdict_from_example(examples[0])
        self.assertTrue(isinstance(verdict, ExceptionVerdict))   
        self.assertTrue(SyntaxError.__name__ in verdict.get_details()) 
    
    def _assert_example_type(self, example_type: Example):
        """Assert that the expected `Example` type is of type the given `example_type`"""
        l1doctests = self.evaluator.get_test_finder().find_l1doctests()
        
        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1)
        L1docTest = l1doctests[0]
        examples = L1docTest.get_examples()
        self.assertTrue(len(examples) == 1) # on assure qu'il existe un seul type Example 
        self.assertTrue(isinstance(examples[0], example_type))
    
    def __build_module_from_source(self, source: str) -> ModuleType:
        """
        Build a module containing the functions declared in the given `source`.
        """
        from types import ModuleType
        fake_module = ModuleType(self.evaluator.get_filename())
        exec(source, fake_module.__dict__)
        return fake_module


if __name__ == '__main__':
    ut.main(verbosity=2)   
        