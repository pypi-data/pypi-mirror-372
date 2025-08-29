import ast
from types import ModuleType
from thonnycontrib.backend.doctest_parser import ExampleExceptionExpected
from thonnycontrib.backend.evaluator import Evaluator
from thonnycontrib.exceptions import *
from thonnycontrib.backend.verdicts.ExceptionVerdict import ExceptionVerdict
from thonnycontrib.backend.verdicts.FailedVerdict import *
from thonnycontrib.backend.verdicts.PassedVerdict import *
from thonnycontrib.backend.verdicts.FailedWhenExceptionExpectedVerdict import FailedWhenExceptionExpectedVerdict
from thonnycontrib.tests.fixtures.backend_mock import *
from thonnycontrib.backend.ast_parser import *

from thonnycontrib.backend.doctest_parser import *
import unittest as ut

# ########################################################
#    Tous les tests qui suivent utilisent l'invite `$$e`
# ########################################################
class TestEvaluator(ut.TestCase):
    def setUp(self):
        self.evaluator = Evaluator(filename="<string>")
        self.mock_backend = backend_patch.start()
        
    def tearDown(self) -> None:
        del self.evaluator   
        backend_patch.stop()
    
    """
    Ce test vérifie:
    1. Le type `ExampleWithExpected` est le type `Example` extrait 
    par le doctest parser.
    2. Si une exception est attendue et que la fonction executée lève 
    cette exception alors on aura un `PassedVerdict`. Enfin, le flag du 
    l1doctest est `PASSED_FLAG`.
    """
    def test_evaluate_when_exception_expected_and_is_raised(self): 
        fake_source = \
"""
def f(a, b):
    '''
    $$e f(-1, -2)
    Exception
    '''
    if a < 0 and b < 0:
        raise Exception("a et b doivent être positifs")
    return a + b
""" 
        
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # ###########################################################
        # ------------- Vérification du type Example ----------------
        self._assert_example_types(ExampleExceptionExpected)
        
        # ###################################################
        # ------------- Vérification du verdict -------------
        l1doctests = self.evaluator.evaluate()
        
        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1)
        l1doctest = l1doctests[0]
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.PASSED_FLAG)
        
        # on assure que le verdict de l'example est un passed verdict
        examples = l1doctest.get_examples()
        self.assertTrue(len(examples) == 1) # on assure qu'il existe un seul Example
        self.assertTrue(isinstance(l1doctest.get_verdict_from_example(examples[0]), PassedVerdict))   
    
    """
    Ce test vérifie:
    1. Le type `ExampleWithExpected` est le type `Example` extrait 
    par le doctest parser.
    2. Si une exception est attendue et que la fonction executée ne lève pas
    cette exception alors on aura un `FailedWhenExceptionExpectedTest`. Enfin,
    le flag du l1doctest est `FAILED_FLAG`.
    """     
    def test_evaluate_when_exception_expected_but_not_raised(self):
        fake_source = \
"""
def f(a, b):
    '''
    $$e f(-1, -2)
    Exception
    '''
    if a < 0 and b < 0:
        return None
    return a + b
""" 
        
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # ###########################################################
        # ------------- Vérification du type Example ----------------
        self._assert_example_types(ExampleExceptionExpected)
        
        # ###################################################
        # ------------- Vérification du verdict -------------
        l1doctests = self.evaluator.evaluate()

        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1)
        l1doctest = l1doctests[0]
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.FAILED_FLAG)
        
        # on assure que le verdict de l'example est en erreur
        examples = l1doctest.get_examples()
        self.assertTrue(len(examples) == 1) # on assure qu'il existe un seul type Example
        
        verdict = l1doctest.get_verdict_from_example(examples[0])
        self.assertTrue(isinstance(verdict, FailedWhenExceptionExpectedVerdict))   
        self.assertTrue("Exception was not raised by `f(-1, -2)`" in verdict.get_details()) 
    
    """
    Ce test vérifie:
    1. Le type `ExampleWithExpected` est le type `Example` extrait 
    par le doctest parser.
    2. Si l'exception attendue n'hérite pas(directement ou indirectement) de 
    la classe `BaseException` alors un verdict de type `ExceptionTest` 
    est renvoyé. Enfin, le flag du l1doctest est `FAILED_FLAG`.
    """        
    def test_evaluate_when_exception_expected_but_dont_inherit_from_base_exception(self):
        
        fake_source = \
"""
class MyException(): pass

def f(a, b):
    '''
    $$e f(-1, -2)
    MyException
    '''
    if a < 0 and b < 0:
        raise MyException()
    return a + b
""" 
        
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # ###########################################################
        # ------------- Vérification du type Example ----------------
        # on assure qu'il existe deux l1doctests (la classe MyException() et la fonction)
        l1doctests = self.evaluator.get_test_finder().find_l1doctests()
        self.assertTrue(len(l1doctests) == 2)
        for l1doctest in l1doctests: 
            if l1doctest.get_type() == ast.FunctionDef.__name__:
                examples = l1doctest.get_examples()
                self.assertTrue(len(examples) == 1) # on assure qu'il existe un seul type Example 
                self.assertTrue(isinstance(examples[0], ExampleExceptionExpected))
        
        # ###################################################
        # ------------- Vérification du verdict -------------
        l1doctests = self.evaluator.evaluate()

        # on assure qu'il existe deux l1doctestz avec ses examples
        self.assertTrue(len(l1doctests) == 2) 
        l1doctest = l1doctests[1] # on récupère le l1doctest de la fonction
        self.assertEqual(l1doctest.get_type(), ast.FunctionDef.__name__)
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.FAILED_FLAG)
        
        # on assure que le verdict de l'example est en erreur
        examples = l1doctest.get_examples()
        self.assertTrue(len(examples) == 1) # on assure qu'il existe un seul type Example
        
        verdict = l1doctest.get_verdict_from_example(examples[0])
        self.assertTrue(isinstance(verdict, ExceptionVerdict))   
        self.assertTrue(TypeError.__name__ in verdict.get_details()) 
        self.assertTrue("is not a class of type exception." in verdict.get_details())
    
    """
    Ce test vérifie:
    1. Le type `ExampleWithExpected` est le type `Example` extrait 
    par le doctest parser.
    2. Si l'exception attendue n'est pas retrouvée(n'est jamais déclarée)
    alors le verdict `ExceptionVerdict` est renvoyé. Enfin, le flag du
    l1doctest est `FAILED_FLAG`.
    """
    def test_evaluate_when_exception_expected_but_is_not_declared(self):    
        fake_source = \
"""
def f(a, b):
    '''
    $$e f(-1, -2)
    UnknownException
    '''
    if a < 0 and b < 0:
        raise Exception()
    return a + b
""" 
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # ###########################################################
        # ------------- Vérification du type Example ----------------
        # on assure qu'il existe seul noeud AST
        self._assert_example_types(ExampleExceptionExpected)
        
        # ###################################################
        # ------------- Vérification du verdict -------------        
        l1doctests = self.evaluator.evaluate()

        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1) 
        l1doctest = l1doctests[0] # on récupère le l1doctest de la fonction
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.FAILED_FLAG)
        
        # on assure que le verdict de l'example est en erreur
        examples = l1doctest.get_examples()
        self.assertTrue(len(examples) == 1) # on assure qu'il existe un seul type Example
        
        verdict = l1doctest.get_verdict_from_example(examples[0])
        self.assertTrue(isinstance(verdict, ExceptionVerdict))   
        self.assertTrue(NameError.__name__ in verdict.get_details()) 
        self.assertTrue("The expected exception `UnknownException` cannot be found." in verdict.get_details())
    
    """
    Ce test vérifie:
    1. Le type `ExampleWithExpected` est le type `Example` extrait 
    par le doctest parser.
    2. Si l'exception attendue n'est pas levée par la fonction executée
    alors le verdict `FailedWhenExceptionExpectedVerdict` est renvoyé. Enfin,
    le flag du l1doctest est `FAILED_FLAG`.
    """        
    def test_evaluate_when_exception_expected_but_an_other_exception_is_raised(self): 
        fake_source = \
"""
def f(a, b):
    '''
    $$e f(-1, -2)
    Exception
    '''
    if a < 0 and b < 0:
        raise ValueError()
    return a + b
""" 
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # ###########################################################
        # ------------- Vérification du type Example ----------------
        # on assure qu'il existe seul noeud AST
        self._assert_example_types(ExampleExceptionExpected)
        
        # ###################################################
        # ------------- Vérification du verdict -------------
        l1doctests = self.evaluator.evaluate()

        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1) 
        l1doctest = l1doctests[0] # on récupère le l1doctest de la fonction
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.FAILED_FLAG)
        
        # on assure que le verdict de l'example est en erreur
        examples = l1doctest.get_examples()
        self.assertTrue(len(examples) == 1) # on assure qu'il existe un seul type Example
        
        verdict = l1doctest.get_verdict_from_example(examples[0])
        self.assertTrue(isinstance(verdict, FailedWhenExceptionExpectedVerdict))   
        self.assertTrue(ValueError.__name__ in verdict.get_details()) 
        self.assertTrue("Exception was not raised by `f(-1, -2)`\nInstead, it raises:" in verdict.get_details())

    """
    Ce test vérifie que le message de l'exception attendu est le même
    que celui de l'erreur qui a vraiment été levée
    """        
    def test_evaluate_when_there_is_expected_message_for_the_expected_exception(self): 
        fake_source = \
"""
def a(n):
    '''
    $$e a(-1)
    ValueError: Mauvais message d'erreur
    '''
    if n < 0:
        raise ValueError("L'argument ne doit pas être inférieur à 0")
    return n
""" 
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # ###########################################################
        # ------------- Vérification du type Example ----------------
        # on assure qu'il existe seul noeud AST
        self._assert_example_types(ExampleExceptionExpected)
        
        # ###################################################
        # ------------- Vérification du verdict -------------
        l1doctests = self.evaluator.evaluate()

        l1doctest = l1doctests[0] # on récupère le l1doctest de la fonction
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.FAILED_FLAG)
        
        # on assure que le verdict de l'example est en erreur
        examples = l1doctest.get_examples()
        
        verdict = l1doctest.get_verdict_from_example(examples[0])
        self.assertTrue(ValueError.__name__ in verdict.get_details()) 
        self.assertTrue("ValueError: Mauvais message d'erreur was not raised by `a(-1)`\n" \
        "Exception was not raised by `a(-1)`\n" \
        "Instead, it raises: ValueError: L'argument ne doit pas être inférieur à 0" in verdict.get_details())

    """
    Ce test vérifie:
    1. Le type `ExampleWithExpected` est le type `Example` extrait 
    par le doctest parser.
    2. Si le test contient une syntaxe erreur alors un verdict `ExceptionVerdict` 
    est renvoyé.
    """       
    def test_evaluate_when_syntax_error(self):
        fake_source = \
"""
def f(a, b):
    '''
    $$e f(-1, -2
    Exception
    '''
    if a < 0 and b < 0:
        raise ValueError()
    return a + b
""" 
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # ###########################################################
        # ------------- Vérification du type Example ----------------
        # on assure qu'il existe seul noeud AST
        self._assert_example_types(ExampleExceptionExpected)
        
        # ###################################################
        # ------------- Vérification du verdict -------------
        l1doctests = self.evaluator.evaluate()

        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1) 
        l1doctest = l1doctests[0] # on récupère le l1doctest de la fonction
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.FAILED_FLAG)
        
        # on assure que le verdict de l'example est en erreur
        examples = l1doctest.get_examples()
        self.assertTrue(len(examples) == 1) # on assure qu'il existe un seul type Example
        
        verdict = l1doctest.get_verdict_from_example(examples[0])
        self.assertTrue(isinstance(verdict, ExceptionVerdict))   
        self.assertTrue(SyntaxError.__name__ in verdict.get_details()) 
    
    """
    Ce test vérifie:
    1. Le type `ExampleWithExpected` est le type `Example` extrait 
    par le doctest parser.
    2. Si le want est un string vide ou un string contenant que des espaces
    alors le verdict `ExceptionVerdict` est renvoyé. Enfin, le flag du
    l1doctest est `FAILED_FLAG`.
    """         
    def test_evaluate_when_exception_is_blank_or_empty(self):
        fake_source = \
"""
def f(a, b):
    '''
    $$e f(-1, -2)   # Example of an empty <want> 
    $$e f(-1, -2)   # Example of a blank <want>
    
    '''
    if a < 0 and b < 0:
        raise Exception()
    return a + b
""" 
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # ###########################################################
        # ------------- Vérification du type Example ----------------
        self._assert_example_types(ExampleExceptionExpected, 2)
        
        # ###################################################
        # ------------- Vérification du verdict -------------
        l1doctests = self.evaluator.evaluate()

        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1) 
        l1doctest = l1doctests[0] # on récupère le l1doctest de la fonction
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.FAILED_FLAG)
        
        # on assure que le verdict de l'example est en erreur
        examples = l1doctest.get_examples()
        self.assertTrue(len(examples) == 2) # on assure qu'il existe un seul type Example
        for example in examples:   
            verdict = example.get_verdict()
            self.assertTrue(isinstance(verdict, ExceptionVerdict))   
            self.assertTrue(ValueError.__name__ in verdict.get_details())  
            self.assertTrue("The expected exception cannot be empty or blank" in verdict.get_details())
    
    
    def _assert_example_types(self, example_type: Example, len_examples=1):
        """
            Assert that the expected `Example` type is of type the given `example_type`.
            Also assert the number of the retrieved examples by given the `len_examples`
            parameter.
        """
        l1doctests = self.evaluator.get_test_finder().find_l1doctests()
        
        # on assure qu'il existe un seul noeud AST
        self.assertTrue(len(l1doctests) == 1)
        for l1_docTest in l1doctests:
            examples = l1_docTest.get_examples()
            self.assertTrue(len(examples) == len_examples) # on assure qu'il existe un seul type Example 
            for i in range(len_examples):
                self.assertTrue(isinstance(examples[i], example_type))
    
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
        