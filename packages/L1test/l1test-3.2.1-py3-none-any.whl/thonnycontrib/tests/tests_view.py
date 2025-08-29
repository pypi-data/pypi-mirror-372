from types import ModuleType
import unittest as ut
from thonnycontrib.backend.ast_parser import L1DocTestFlag
from thonnycontrib.backend.verdicts.PassedSetupVerdict import PassedSetupVerdict
from thonnycontrib.frontend.l1test_treeview import L1TestTreeView
from thonnycontrib.backend.evaluator import Evaluator
from thonnycontrib.exceptions import *
from thonnycontrib.backend.verdicts.FailedWhenExceptionExpectedVerdict import FailedWhenExceptionExpectedVerdict
from thonnycontrib.backend.verdicts.ExceptionVerdict import ExceptionVerdict
from thonnycontrib.backend.verdicts.FailedVerdict import FailedVerdict
from thonnycontrib.backend.verdicts.PassedVerdict import PassedVerdict
from thonnycontrib.backend.doctest_parser import *
from unittest.mock import *
from thonnycontrib.tests.fixtures.backend_mock import *

# #######################################################
#    Tous les tests qui suivent vérifient le rendu ur la treeview
# #######################################################


# ######## ATTENTION : NOTE IMPORTANTE ##################
# Dans les tests suivants, on assure la présence du verdict pour les setups qui réussissent (PassedSetupVerdict),
# mais en réalité leurs verdicts ne sont pas affichés sur la vue. Ils sont filtrés dans la méthode _add_verdicts_to_node() 
# de la classe L1TestTreeView.
# #######################################################

class MockL1TestTreeView(L1TestTreeView):
    def __init__(self):
        pass
        
class TestTestReporter(ut.TestCase):
    def setUp(self):
        self.l1TestTreeview = MockL1TestTreeView()
        self.evaluator = Evaluator(filename="<string>")
        self.mock_backend = backend_patch.start()
    
    def tearDown(self) -> None:
        del self.evaluator
        backend_patch.stop()
    
    def test_summarize_case_1(self):
        fake_source = \
"""
def f(a, b):
    '''
    $$$ f(1, 1)     # Passed verdict
    2
    $$$ f(1, 1)     # Failed verdict
    0
    $$$ f(20, 20)   # Exception verdict
    0
    $$$ l = []      # It's a setup -> no verdict
    '''
    if a < 0 and b < 0:
        return None
    if a > 10 and b > 10:
        raise ValueError()
    return a + b
"""
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # #####################################################
        # ------------- Verification des verdicts -------------
        expected_verdicts_colors = {PassedVerdict: "green",
                                    FailedVerdict: "red",
                                    ExceptionVerdict: "red",
                                    PassedSetupVerdict: "black"}
        
        l1doctests = self.evaluator.evaluate()
        
        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1)
        l1doctest = l1doctests[0]
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué

        examples = l1doctest.get_examples() 
        # on s'assure que le nombre de verdicts calculés est exactement le nombre de verdicts attendus
        self.assertEqual(len(examples), len(expected_verdicts_colors)) 
        # on assure que les verdicts récupérés sont exactement les verdicts attendus
        self.assertEqual([e.get_verdict().__class__ for e in examples], list(expected_verdicts_colors.keys()))

        # ##################################################################
        # ------------- Verification des couleurs des verdicts -------------
        self.assertEqual([e.get_verdict().get_color() for e in examples], list(expected_verdicts_colors.values())) 
        
        # ##################################################################
        # ------------------ Verification du SUMMARIZE ---------------------
        summarize = self.l1TestTreeview.build_summarize_object(l1doctests)
        self.assertTrue(summarize.total == 3) 
        self.assertTrue(summarize.success == 1) 
        self.assertTrue(summarize.failures == 1) 
        self.assertTrue(summarize.errors == 1) 
        self.assertTrue(summarize.empty == 0)
        
        # ###########################################################################
        # ------------------ Verification du status du l1doctest ---------------------
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.FAILED_FLAG)
        self.assertEqual(l1doctest.get_flag().get_color(), "red")
    
    def test_summarize_case_2(self):
        """
        Dans ce test on vérifie le résultat de summarize quand la docstring 
        contient que des setups.
        """
        fake_source = \
"""
def f(a, b):
    '''
    $$$ a = 0 
    '''
    return a + b
"""
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # #####################################################
        # ------------- Verification des verdicts -------------        
        l1doctests = self.evaluator.evaluate()
        
        # on s'assure qu'il existe un seul noeud AST 
        self.assertEqual(len(l1doctests), 1)
        
        l1doctest = l1doctests[0]
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual([PassedSetupVerdict], [e.get_verdict().__class__ for e in l1doctest.get_examples()]) 
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.EMPTY_FLAG)
        self.assertEqual(l1doctest.get_flag().get_color(), "orange")
        
        # ##################################################################
        # ------------------ Verification du SUMMARIZE ---------------------
        summarize = self.l1TestTreeview.build_summarize_object(l1doctests)
        self.assertTrue(summarize.empty == 1)
        self.assertTrue(summarize.total == 0) 
        self.assertTrue(summarize.success == 0) 
        self.assertTrue(summarize.failures == 0) 
        self.assertTrue(summarize.errors == 0) 
            
    def test_summarize_case_3(self):
        """
        Dans ce test on vérifie le résultat de summarize quand la docstring 
        contient à la fois des setups et des tests.
        """
        fake_source = \
"""
def f(a, b):
    '''
    $$$ a = 1 
    $$$ b = 1
    $$$ f(a, b)
    2
    '''
    return a + b
"""
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # #####################################################
        # ------------- Verification des verdicts -------------
        expected_verdicts = [PassedSetupVerdict, PassedSetupVerdict, PassedVerdict]
        expected_verdicts_colors = ["black", "black", "green"]
        
        l1doctests = self.evaluator.evaluate()
        
        # on assure qu'il existe un seul l1doctest avec ses examples
        self.assertTrue(len(l1doctests) == 1)
        l1doctest = l1doctests[0]
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué

        examples = l1doctest.get_examples() 
        # on s'assure que le nombre de verdicts calculés est exactement le nombre de verdicts attendus
        self.assertEqual(len(examples), len(expected_verdicts)) 
        # on assure que les verdicts récupérés sont exactement les verdicts attendus
        self.assertEqual([e.get_verdict().__class__ for e in examples], expected_verdicts)

        # ##################################################################
        # ------------- Verification des couleurs des verdicts -------------
        self.assertEqual([e.get_verdict().get_color() for e in examples], expected_verdicts_colors) 
        
        # ##################################################################
        # ------------------ Verification du SUMMARIZE ---------------------
        summarize = self.l1TestTreeview.build_summarize_object(l1doctests)
        self.assertTrue(summarize.total == 1) 
        self.assertTrue(summarize.success == 1)  
        self.assertTrue(summarize.failures == 0) 
        self.assertTrue(summarize.errors == 0) 
        self.assertTrue(summarize.empty == 0)
        
        # ###########################################################################
        # ------------------ Verification du status du l1doctest ---------------------
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.PASSED_FLAG)
        self.assertEqual(l1doctest.get_flag().get_color(), "green")
        
    def test_summarize_case_4(self):
        """
        Dans ce test on vérifie le résultat de summarize quand 
        il existe 2 noeuds ast dont un d'eux contient que des setups 
        et l'autre contient des tests.
        """
        fake_source = \
"""
def minus(a, b):
    '''
    $$$ a = 1
    '''
    return a - b
    
def somme(a, b):
    '''
    $$$ a = 1
    $$$ b = 1
    $$$ somme(a, b)
    2
    '''
    return a + b
"""
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # #####################################################
        # ------------- Verification des verdicts -------------
        l1doctests = self.evaluator.evaluate()
        
        # on assure qu'il existe 2 l1doctests 
        self.assertTrue(len(l1doctests) == 2)
        
        # ---- vérification pour `minus()` ---
        l1doctest = l1doctests[0]
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertTrue("minus" in l1doctest.get_name())
        examples = l1doctest.get_examples()
        self.assertEqual(len(l1doctest.get_examples()), 1) 
        self.assertEqual([PassedSetupVerdict], [e.get_verdict().__class__ for e in examples])
        # le flag est `EMPTY_FLAG` car il n'y a pas de tests pour `minus()`
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.EMPTY_FLAG)

        # ---- vérification pour `somme()` ---
        l1doctest = l1doctests[1]
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertTrue("somme" in l1doctest.get_name())
        examples = l1doctest.get_examples()
        self.assertEqual(len(examples), 3) 
        self.assertEqual([PassedSetupVerdict, PassedSetupVerdict, PassedVerdict], 
                         [e.get_verdict().__class__ for e in examples])
        self.assertEqual(["black", "black", "green"], 
                         [e.get_verdict().get_color() for e in examples])
        # le flag est `PASSED_FLAG` car il existe un test qui passe pour `somme()`
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.PASSED_FLAG)
        
        # ##################################################################
        # ------------------ Verification du SUMMARIZE ---------------------
        summarize = self.l1TestTreeview.build_summarize_object(l1doctests)
        self.assertTrue(summarize.total == 1) 
        self.assertTrue(summarize.success == 1) 
        self.assertTrue(summarize.failures == 0) 
        self.assertTrue(summarize.errors == 0) 
        self.assertTrue(summarize.empty == 1) 
    
    def test_summarize_case_5(self):
        """
        Dans ce test on vérifie le résultat de summarize quand 
        l'invite est `$$e`.
        """
        fake_source = \
"""
class NotAnException: pass

def somme(a, b):
    '''
    $$e somme(10, 10)       # le cas qui échoue(failed verdict)
    ValueError
    
    $$$ a, b = -1, -1
    $$e somme(a, b)         # le cas qui passe
    ValueError
    $$e somme(a, b)         
    UndefinedException      # le want déclare une exception qui n'existe pas
    $$e somme(a, b)
    Invalid name            # le want contient une erreur de nommage
    $$e somme(a, b)
    NotAnException          # le want n'est pas une exception qui hérite de BaseException
    '''
    if a > 9  or b > 9:
        raise Exception("a et b doivent être que des chiffres")
    if a < 0 and b < 0:
        raise ValueError()
    return a + b
"""
        self.evaluator.set_source(fake_source)
        self.evaluator.set_module(self.__build_module_from_source(fake_source))
        
        # #####################################################
        # ------------- Verification des verdicts -------------
        l1doctests = self.evaluator.evaluate()
        
        # on s'assure qu'il existe deux noeuds AST : la fonction `somme()` et la classe `NotAnException`
        self.assertEqual(len(l1doctests), 2)
        
        # ---- vérification pour le l1Doctest correpondant à la classe `NotAnException` ---
        l1doctest = l1doctests[0] # le l1doctest de la classe `NotAnException`
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.EMPTY_FLAG)
        self.assertEqual(l1doctest.get_flag().get_color(), "orange")
        
        # ---- vérification pour le l1Doctest correpondant à la fonction `somme()` ---
        expected_verdicts = [FailedWhenExceptionExpectedVerdict, PassedSetupVerdict, PassedVerdict] + \
                            [ExceptionVerdict]*3  # there are 3 exceptions verdicts
        expected_colors = ["red", "black", "green"] + ["red"]*3
        
        l1doctest = l1doctests[1] # le l1doctest de la fonction `somme()`
        self.assertTrue(l1doctest.is_evaluated()) # s'assure que le l1doctest a été évalué
        self.assertEqual(l1doctest.get_flag(), L1DocTestFlag.FAILED_FLAG)
        self.assertEqual(l1doctest.get_flag().get_color(), "red")
        
        examples = l1doctest.get_examples()
        self.assertEqual(expected_verdicts, [e.get_verdict().__class__ for e in examples])
        self.assertEqual(expected_colors, [e.get_verdict().get_color() for e in examples])
        
        # ##################################################################
        # ------------------ Verification du SUMMARIZE ---------------------
        summarize = self.l1TestTreeview.build_summarize_object(l1doctests)  
        self.assertTrue(summarize.total == 5) 
        self.assertTrue(summarize.success == 1)  
        self.assertTrue(summarize.failures == 1) 
        self.assertTrue(summarize.errors == 3) 
        self.assertTrue(summarize.empty == 1)

             
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
        
