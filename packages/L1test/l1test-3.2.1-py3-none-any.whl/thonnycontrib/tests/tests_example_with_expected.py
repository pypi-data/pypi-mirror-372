from types import ModuleType
from thonnycontrib.backend.ast_parser import L1DocTestFlag
from thonnycontrib.backend.doctest_parser import ExampleWithExpected
from thonnycontrib.backend.evaluator import Evaluator
from thonnycontrib.exceptions import *
from thonnycontrib.backend.verdicts.ExceptionVerdict import ExceptionVerdict
from thonnycontrib.backend.verdicts.FailedVerdict import FailedVerdict
from thonnycontrib.backend.verdicts.PassedVerdict import PassedVerdict
from thonnycontrib.backend.doctest_parser import *
import unittest as ut
from thonnycontrib.tests.fixtures.backend_mock import *

# ########################################################
#    Tous les tests qui suivent utilisent l'invite `$$$`
#               AVEC une valeur attendue  
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
    1. Quand il n'y a aucun test dans une docstring alors aucun 
    type Example n'est produit. On assure plutôt que la liste
    d'Example associée au noeud est vide.
    2. Lorsqu'un l1doctest ne contient aucun test alors assurer
    que son flag est EMPTY_FLAG
    """
    def test_evaluate_when_empty_verdict(self):
        fake_source = \
"""
def f(a, b):
    if a < 0 and b < 0:
        return None
    return a + b
"""
        
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # ###################################################
        # ------------- Vérification du verdict -------------
        l1doctests = self.evaluator.evaluate()
        
        # on assure qu'il existe un seul l1doctest
        self.assertTrue(len(l1doctests) == 1)
        l1doctest = l1doctests[0]
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.EMPTY_FLAG)
        
        # on assure qu'il n'y a aucun example
        self.assertTrue(len(l1doctest.get_examples()) == 0) 
    
    """
    Ce test vérifie:
    1. Le type `ExampleWithExpected` est le type `Example` extrait 
    par le doctest parser.
    2. Le verdict renvoyé est de type `PassedTest`. 
    """     
    def test_evaluate_when_passed_verdict(self):
        fake_source = \
"""
def f(a, b):
    '''
    $$$ f(1, 2)
    3
    '''
    if a < 0 and b < 0:
        return None
    return a + b
""" 
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # ###########################################################
        # ------------- Vérification du type Example ----------------
        self._assert_example_type(ExampleWithExpected)
        
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
    2. Quand un test échoue et que le résultat réél est un string vide,
    alors on assure que le message d'echec inclut une chaine viee. Ce test
    a été ajouté pour corriger le bug (issue #15, sur le lien suivant:
    https://gitlab.univ-lille.fr/mirabelle.nebut/thonny-tests/-/issues/15)
    """
    def test_evaluate_and_check_string_when_failed(self):
        fake_source = \
"""
def foo():
    '''
    $$$ foo()
    'a'
    '''
    return ''
""" 
        
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # ###########################################################
        # ------------- Vérification du type Example ----------------
        self._assert_example_type(ExampleWithExpected)
        
        # ###################################################
        # ------------- Vérification du verdict -------------
        l1doctests = self.evaluator.evaluate()
        
        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1)
        l1doctest = l1doctests[0]
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.FAILED_FLAG)
        
        examples = l1doctest.get_examples()
        self.assertTrue(len(examples) == 1) 
        verdict = l1doctest.get_verdict_from_example(examples[0])
        self.assertTrue(isinstance(verdict, FailedVerdict))
        self.assertTrue("Expected: 'a', Got: ''" in verdict.get_details())
    
    """
    Ce test vérifie:
    1. Le type `ExampleWithExpected` est le type `Example` extrait 
    par le doctest parser.
    2. Quand un test échoue et que le résultat réél est de type `str`,
    alors on assure que le message inclut bien les quotes. Ce test
    a été ajouté pour corriger le bug (issue #13, sur le lien suivant:
    https://gitlab.univ-lille.fr/mirabelle.nebut/thonny-tests/-/issues/13)
    """
    def test_evaluate_and_check_string_when_failed(self): 
        fake_source = \
"""
def toto():
    '''
    $$$ toto()
    "titi"
    '''
    return 'toto'
""" 
        
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # ###########################################################
        # ------------- Vérification du type Example ----------------
        self._assert_example_type(ExampleWithExpected)
        
        # ###################################################
        # ------------- Vérification du verdict -------------
        l1doctests = self.evaluator.evaluate()
        
        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1)
        l1doctest = l1doctests[0]
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.FAILED_FLAG)
        
        examples = l1doctest.get_examples()
        self.assertTrue(len(examples) == 1) 
        verdict = l1doctest.get_verdict_from_example(examples[0])
        self.assertTrue(isinstance(verdict, FailedVerdict))
        
        self.assertTrue("Expected: \"titi\", Got: 'toto'" in verdict.get_details())


    def test_evaluate_and_check_empty_string_when_failed(self): 
        fake_source = \
"""
def toto():
    '''
    $$$ toto()
    "titi"
    '''
    return ''
""" 
        
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # ###########################################################
        # ------------- Vérification du type Example ----------------
        self._assert_example_type(ExampleWithExpected)
        
        # ###################################################
        # ------------- Vérification du verdict -------------
        l1doctests = self.evaluator.evaluate()
        
        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1)
        l1doctest = l1doctests[0]
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.FAILED_FLAG)
        
        examples = l1doctest.get_examples()
        self.assertTrue(len(examples) == 1) 
        verdict = l1doctest.get_verdict_from_example(examples[0])
        self.assertTrue(isinstance(verdict, FailedVerdict))
        
        self.assertTrue("Expected: \"titi\", Got: ''" in verdict.get_details())
    
    """
    Ce test vérifie:
    1. Le type `ExampleWithExpected` est le type `Example` extrait 
    par le doctest parser.
    2. Le verdict renvoyé est de type `FailedTest`. Enfin, on assure
    que le flag du l1doctest est FAILED_FLAG.
    """
    def test_evaluate_when_failed_verdict(self):
        fake_source = \
"""
def f(a, b):
    '''
    $$$ f(1, 2)
    2
    '''
    if a < 0 and b < 0:
        return None
    return a + b
""" 
        
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # ###########################################################
        # ------------- Vérification du type Example ----------------
        self._assert_example_type(ExampleWithExpected)
        
        # ###################################################
        # ------------- Vérification du verdict -------------
        l1doctests = self.evaluator.evaluate()
        
        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1)
        l1doctest = l1doctests[0]
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.FAILED_FLAG)
        
        examples = l1doctest.get_examples()
        self.assertTrue(len(examples) == 1) 
        verdict = l1doctest.get_verdict_from_example(examples[0])
        self.assertTrue(isinstance(verdict, FailedVerdict))
        self.assertTrue(verdict.details == '3')
        self.assertTrue('Expected: 2, Got: 3' in verdict.get_details())
    
    """
    Ce test vérifie:
    1. Le type `ExampleWithExpected` est le type `Example` extrait 
    par le doctest parser.
    2. Le verdict renvoyé est de type `ExceptionTest` car la 
    comparaison `if a < 0 and b < 0:` va échouer si l'argument `a` ou `b`
    ne sont pas de type `int`. Enfin, on assure que le flag du l1doctest
    est FAILED_FLAG.
    """
    def test_evaluate_when_exception_verdict(self):
        fake_source = \
"""
def f(a, b):
    '''
    $$$ f('j', 2)
    2
    '''
    if a < 0 and b < 0:
        return None
    return a + b
""" 
        
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # ###########################################################
        # ------------- Vérification du type Example ----------------
        self._assert_example_type(ExampleWithExpected)
        
        # ###################################################
        # ------------- Vérification du verdict -------------
        l1doctests = self.evaluator.evaluate()
        
        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1)
        l1doctest = l1doctests[0]
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.FAILED_FLAG)
        
        examples = l1doctest.get_examples()
        self.assertTrue(len(examples) == 1) 
        verdict = l1doctest.get_verdict_from_example(examples[0])
        self.assertTrue(isinstance(verdict, ExceptionVerdict))
        self.assertTrue("TypeError: '<' not supported between instances of 'str' and 'int'"\
                            in verdict.get_details())
    
    """
    Ce test vérifie:
    1. Le type `ExampleWithExpected` est le type `Example` extrait 
    par le doctest parser.
    2. Quand la valeur attendue est None et que la fonction executée renvoie None
    alors on aura un verdict de type `PassedTest`. Le flag du l1doctest est 
    PASSED_FLAG.
    """    
    def test_evaluate_when_expected_is_none(self):
        fake_source = \
"""
def f(a, b):
    '''
    $$$ f(-1, -1)
    None
    '''
    if a < 0 and b < 0:
        return None
    return a + b
""" 
        
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # ###########################################################
        # ------------- Vérification du type Example ----------------
        self._assert_example_type(ExampleWithExpected)
        
        # ###################################################
        # ------------- Vérification du verdict -------------
        l1doctests = self.evaluator.evaluate()
        
        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1)
        l1doctest = l1doctests[0]
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.PASSED_FLAG)
        
        examples = l1doctest.get_examples()
        self.assertTrue(len(examples) == 1) 
        self.assertTrue(isinstance(l1doctest.get_verdict_from_example(examples[0]), PassedVerdict))
    
    """
    Ce test vérifie:
    1. Le type `ExampleWithExpected` est le type `Example` extrait 
    par le doctest parser.
    2. Quand il y a une erreur de syntax au niveau du test alors
    un verdict `ExceptionTest` est renvoyé. ENfin, on assure que le flag
    du l1doctest est FAILED_FLAG.
    """
    def test_evaluate_when_syntax_error(self):
        fake_source = \
"""
def f(a, b):
    '''
    $$$ f(1, 1
    2
    '''
    if a < 0 and b < 0:
        return None
    return a + b
""" 
        
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # ###########################################################
        # ------------- Vérification du type Example ----------------
        self._assert_example_type(ExampleWithExpected)
        
        # ###################################################
        # ------------- Vérification du verdict -------------
        l1doctests = self.evaluator.evaluate()
        
        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1)
        l1doctest = l1doctests[0]
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.FAILED_FLAG)
        
        examples = l1doctest.get_examples()
        self.assertTrue(len(examples) == 1) 
        verdict = l1doctest.get_verdict_from_example(examples[0])
        self.assertTrue(isinstance(verdict, ExceptionVerdict))
        self.assertTrue(SyntaxError.__name__ in verdict.get_details())
    
    """
    Ce test vérifie:
    1. Le type `ExampleWithExpected` est le type `Example` extrait 
    par le doctest parser.
    2. Quand la fonction executée utilise une variable non déclarée alors
    on assure que le verdict est de type `ExceptionTest`
    """
    def test_evaluate_when_runtime_error(self):
        fake_source = \
"""
def f(a, b):
    '''
    $$$ f(1, 1)
    2
    '''
    if a < 0 and b < 0:
        return None
    return a + b * c
""" 
        
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # ###########################################################
        # ------------- Vérification du type Example ----------------
        self._assert_example_type(ExampleWithExpected)
        
        # ###################################################
        # ------------- Vérification du verdict -------------
        l1doctests = self.evaluator.evaluate()
        
        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1)
        l1doctest = l1doctests[0]
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.FAILED_FLAG)
        
        examples = l1doctest.get_examples()
        self.assertTrue(len(examples) == 1) 
        verdict = l1doctest.get_verdict_from_example(examples[0])
        self.assertTrue(isinstance(verdict, ExceptionVerdict))
        self.assertTrue(NameError.__name__ in verdict.get_details())
        self.assertTrue("name 'c' is not defined" in verdict.get_details())  
    
    """
    Ce test vérifie:
    1. Le type `ExampleWithExpected` est le type `Example` extrait 
    par le doctest parser.
    2. Quand la valeur attendue est une exception et que la fonction lève 
    une exception alors on aura le verdict `ExceptionTest`.
    """      
    def test_evaluate_when_an_exception_is_expected_and_raised(self):
        fake_source = \
"""
def f(a, b):
    '''
    $$$ f(-1, -1)
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
        self._assert_example_type(ExampleWithExpected)
        
        # ###################################################
        # ------------- Vérification du verdict -------------
        l1doctests = self.evaluator.evaluate()
        
        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1)
        l1doctest = l1doctests[0]
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.FAILED_FLAG)
        
        examples = l1doctest.get_examples()
        self.assertTrue(len(examples) == 1) 
        verdict = l1doctest.get_verdict_from_example(examples[0])
        self.assertTrue(isinstance(verdict, ExceptionVerdict))
        self.assertTrue(Exception.__name__ in verdict.get_details())
        self.assertTrue("a et b doivent être positifs" in verdict.get_details()) 

    """
    Ce test vérifie:
    1. Le type `ExampleWithExpected` est le type `Example` extrait 
    par le doctest parser.
    2. Quand la valeur attendue est une exception mais la fonction ne lève pas
    une exception, dans ce cas on aura le verdict `FailedTest`.
    """        
    def test_evaluate_when_an_exception_is_expected_but_not_raised(self):
        fake_source = \
"""
def f(a, b):
    '''
    $$$ f(-1, -1)
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
        self._assert_example_type(ExampleWithExpected)
        
        # ###################################################
        # ------------- Vérification du verdict -------------
        l1doctests = self.evaluator.evaluate()
        
        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1)
        l1doctest = l1doctests[0]
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.FAILED_FLAG)
        
        examples = l1doctest.get_examples()
        self.assertTrue(len(examples) == 1) 
        verdict = l1doctest.get_verdict_from_example(examples[0])
        self.assertTrue(isinstance(verdict, FailedVerdict))
        self.assertTrue(Exception.__name__ in verdict.get_details())
        self.assertTrue('Expected: Exception, Got: None' in verdict.get_details())
    
    """
    Ce test vérifie:
    1. Le type `ExampleWithoutExpected` est le type `Example` extrait 
    par le doctest parser.
    2. si un test est setup mais il existe quand même une valeur attendue
    alors le verdict renvoyée est de type `ExceptionTest`
    """
    def test_evaluate_when_setup(self):
        fake_source = \
"""
def f(a, b):
    '''
    $$$ a = 0
    0
    '''
    if a < 0 and b < 0:
        return None
    return a + b
""" 
        
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # ###########################################################
        # ------------- Vérification du type Example ----------------
        self._assert_example_type(ExampleWithExpected)
        
        # ###################################################
        # ------------- Vérification du verdict -------------
        l1doctests = self.evaluator.evaluate()
        
        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1)
        l1doctest = l1doctests[0]
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.FAILED_FLAG)
        
        examples = l1doctest.get_examples()
        self.assertTrue(len(examples) == 1) 
        verdict = l1doctest.get_verdict_from_example(examples[0])
        self.assertTrue(isinstance(verdict, ExceptionVerdict))
        self.assertTrue(SyntaxError.__name__ in verdict.get_details())
        self.assertTrue("invalid syntax. Maybe you meant '==' or ':=' instead of '='?"\
                            in verdict.get_details())
    
    
    def _assert_example_type(self, example_type: Example):
        """Assert that the expected `Example` type is of type the given `example_type`"""
        l1doctests = self.evaluator.get_test_finder().find_l1doctests()
        
        # on assure qu'il existe un seul l1doctest
        self.assertTrue(len(l1doctests) == 1)
        for l1_docTest in l1doctests:
            examples = l1_docTest.get_examples()
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
        
