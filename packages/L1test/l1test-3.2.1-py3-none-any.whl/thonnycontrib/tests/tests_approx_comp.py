from types import ModuleType
from thonnycontrib.backend.ast_parser import L1DocTestFlag
from thonnycontrib.backend.doctest_parser import ExampleWithExpected
from thonnycontrib.backend.evaluator import Evaluator
from thonnycontrib.exceptions import *
from thonnycontrib.backend.verdicts.ExceptionVerdict import ExceptionVerdict
from thonnycontrib.backend.verdicts.FailedVerdict import FailedVerdict
from thonnycontrib.backend.verdicts.PassedVerdict import PassedVerdict
from thonnycontrib.backend.doctest_parser import *
from thonnycontrib.backend.approx_comp import approx, ApproxSimple, DEFAULT_TOLERANCE, ApproxList, ApproxDict, ApproxTuple
import unittest
from thonnycontrib.tests.fixtures.backend_mock import backend_patch

class TestApprox(unittest.TestCase):

    def test_evaluate_plain_float_approx_comparison_tolerance_given(self):
        self.assertTrue(abs(3.312 - 3.31) <= 0.1)
        self.assertTrue(3.312 == approx(3.31, 0.1))

        self.assertFalse(abs(3.3 - 3.4) <= 0.1)
        self.assertFalse(3.3 == approx(3.4, 0.1))

        self.assertTrue(abs(0.1 + 0.2 - 0.3) <= 1e-5)
        self.assertTrue(0.1 + 0.2 == approx(0.3, 1e-5))
        
        self.assertFalse(abs(0.1 + 0.2 - 0.3) <= 1e-20)
        self.assertFalse(0.1 + 0.2 == approx(0.3, 1e-20))

        self.assertFalse(3.3 == approx(3.5, 0.1))


    def test_evaluate_plain_int_approx_comparison_tolerance_given(self):
        self.assertTrue(abs(3 - 4) <= 1)
        self.assertTrue(3 == approx(4, 1))

        self.assertTrue(abs(3 - 4) <= 2)
        self.assertTrue(3 == approx(4, 2))

        self.assertFalse(abs(3 - 4) <= 0)
        self.assertFalse(3 == approx(4, 0))

        
    def test_evaluate_plain_float_approx_comparison_default_tolerance(self):
        self.assertFalse(abs(3.3 - 3.5) <= DEFAULT_TOLERANCE)
        self.assertFalse(3.3 == approx(3.5))

        self.assertTrue(abs(0.1 + 0.2 - 0.3) <= DEFAULT_TOLERANCE)
        self.assertTrue(0.1 + 0.2 == approx(0.3))

        self.assertFalse(abs(0.1 + DEFAULT_TOLERANCE - 0.1) <= DEFAULT_TOLERANCE)
        self.assertFalse(0.1 + DEFAULT_TOLERANCE == approx(0.1))

    def test_evaluate_plain_int_approx_comparison_default_tolerance(self):
        self.assertTrue(2 == approx(2))
        self.assertFalse(2 == approx(3))

    def test_repr_simple(self):
        ap_default = ApproxSimple(3.3)
        self.assertEqual(str(ap_default), "3.3 +- 1e-06")

        ap = ApproxSimple(3.3, 1e-12)
        self.assertEqual(str(ap), "3.3 +- 1e-12")

    def test_repr_list(self):
        ap = ApproxList([1, 4.3, True])
        self.assertEqual(str(ap), "[1, 4.3, True] +- 1e-06")

    def test_repr_dict(self):
        ap = ApproxDict({"one": 1.3, "two": 2.4, "three": 3.5})
        self.assertEqual(str(ap), "{'one': 1.3, 'two': 2.4, 'three': 3.5} +- 1e-06")

    def test_repr_tuple(self):
        ap = ApproxTuple((5.5, 6.6, 7.8))
        self.assertEqual(str(ap), "(5.5, 6.6, 7.8) +- 1e-06")



    def test_bad_approx_type_raises_exception(self):
        self.assertRaises(TypeError, approx, "go")

        # Malheureusement... isinstance(True, int) est vrai
        self.assertFalse(3 == approx(True))

        self.assertRaises(TypeError, approx, [[]])
        self.assertRaises(TypeError, approx, [1.1, "ert", 5])

    def test_negative_tolerance_raises_exception(self):
        self.assertRaises(ValueError, approx, 3.3, -1e-5)

    def test_evaluate_list_approx_comparison_tolerance_given(self):
        # tous approchés OK
        l1 = [0.1 + 0.2, 0.1 + 0.2, 0.1 + 0.2]
        l2 = [0.3, 0.3, 0.3]
        self.assertTrue(l1 == approx(l2, 1e-5))
        # aucun approché OK
        l1 = [0.1 + 0.2, 0.1 + 0.2, 0.1 + 0.2]
        l2 = [0.3, 0.3, 0.3]
        self.assertFalse(l1 == approx(l2, 1e-20))
        # un approché KO, au milieu
        l1 = [0.1 + 0.2, 0.1 + 0.2, 0.1 + 0.2]
        l2 = [0.3, 0.4, 0.3]
        self.assertFalse(l1 == approx(l2, 1e-5))
        # un approché KO, au début
        l1 = [0.1 + 0.2, 0.1 + 0.2, 0.1 + 0.2]
        l2 = [0.4, 0.3, 0.3]
        self.assertFalse(l1 == approx(l2, 1e-5))
        # un approché KO à la fin
        l1 = [0.1 + 0.2, 0.1 + 0.2, 0.1 + 0.2]
        l2 = [0.3, 0.3, 0.4]
        self.assertFalse(l1 == approx(l2, 1e-5))
        # liste singleton
        l1 = [0.1 + 0.2]
        l2 = [0.3]
        self.assertTrue(l1 == approx(l2, 1e-5))
        # liste vide
        l1 = []
        l2 = []
        self.assertTrue(l1 == approx(l2, 1e-5))
    
    def test_evaluate_list_approx_comparison_default_tolerance(self):
        # tous approchés OK
        l1 = [0.1 + 0.2, 0.1 + 0.2, 0.1 + 0.2]
        l2 = [0.3, 0.3, 0.3]
        self.assertTrue(l1 == approx(l2))
        # aucun approché OK
        l1 = [0.1 + 0.2, 0.1 + 0.2, 0.1 + 0.2]
        l2 = [0.3, 0.3, 0.3]
        self.assertTrue(l1 == approx(l2))
        # un approché KO, au milieu
        l1 = [0.1 + 0.2, 0.1 + 0.2, 0.1 + 0.2]
        l2 = [0.3, 0.4, 0.3]
        self.assertFalse(l1 == approx(l2))
        # un approché KO, au début
        l1 = [0.1 + 0.2, 0.1 + 0.2, 0.1 + 0.2]
        l2 = [0.4, 0.3, 0.3]
        self.assertFalse(l1 == approx(l2))
        # un approché KO à la fin
        l1 = [0.1 + 0.2, 0.1 + 0.2, 0.1 + 0.2]
        l2 = [0.3, 0.3, 0.4]
        self.assertFalse(l1 == approx(l2))
        # liste singleton
        l1 = [0.1 + 0.2]
        l2 = [0.3]
        self.assertTrue(l1 == approx(l2))
        # liste vide
        l1 = []
        l2 = []
        self.assertTrue(l1 == approx(l2))

    def test_evaluate_tuple_approx_comparison_tolerance_given(self):
        # tous approchés OK
        t1 = (0.1 + 0.2, 0.1 + 0.2, 0.1 + 0.2)
        t2 = (0.3, 0.3, 0.3)
        self.assertTrue(t1 == approx(t2, 1e-5))
        # aucun approché OK
        t1 = (0.1 + 0.2, 0.1 + 0.2, 0.1 + 0.2)
        t2 = (0.3, 0.3, 0.3)
        self.assertFalse(t1 == approx(t2, 1e-20))
        # un approché KO, au milieu
        t1 = (0.1 + 0.2, 0.1 + 0.2, 0.1 + 0.2)
        t2 = (0.3, 0.4, 0.3)
        self.assertFalse(t1 == approx(t2, 1e-5))
        #tuple singleton
        t1 = (0.1 + 0.2)
        t2 = (0.3)
        self.assertTrue(t1 == approx(t2, 1e-5))
        #tuple vide
        t1 = ()
        t2 = ()
        self.assertTrue(t1 == approx(t2, 1e-5))

    def test_evaluate_tuple_approx_comparison_default_tolerance(self):
        # tous approchés OK
        t1 = (0.1 + 0.2, 0.1 + 0.2, 0.1 + 0.2)
        t2 = (0.3, 0.3, 0.3)
        self.assertTrue(t1 == approx(t2))
        # aucun approché OK
        t1 = (0.1 + 0.2, 0.1 + 0.2, 0.1 + 0.2)
        t2 = (0.3, 0.3, 0.3)
        self.assertTrue(t1 == approx(t2))
        # un approché KO, au milieu
        t1 = (0.1 + 0.2, 0.1 + 0.2, 0.1 + 0.2)
        t2 = (0.3, 0.4, 0.3)
        self.assertFalse(t1 == approx(t2))
        #tuple singleton
        t1 = (0.1 + 0.2,)
        t2 = (0.3,)
        self.assertTrue(t1 == approx(t2))
        #tuple vide
        t1 = ()
        t2 = ()
        self.assertTrue(t1 == approx(t2))

    def test_evaluate_dict_approx_comparison_tolerance_given(self):
        # tous approchés OK
        d1 = {"a": 0.1 + 0.2, "b": 0.1 + 0.2, "c": 0.1 + 0.2}
        d2 = {"a": 0.3, "b": 0.3, "c": 0.3}
        self.assertTrue(d1 == approx(d2, 1e-5))
        # aucun approché OK
        d1 = {"a": 0.1 + 0.2, "b": 0.1 + 0.2, "c": 0.1 + 0.2}
        d2 = {"a": 0.3, "b": 0.3, "c": 0.3}
        self.assertFalse(d1 == approx(d2, 1e-20))
        # un approché KO, au milieu
        d1 = {"a": 0.1 + 0.2, "b": 0.1 + 0.2, "c": 0.1 + 0.2}
        d2 = {"a": 0.3, "b": 0.4, "c": 0.3}
        self.assertFalse(d1 == approx(d2, 1e-5))
        #dictionnaire singleton
        d1 = {"a": 0.1 + 0.2}
        d2 = {"a": 0.3}
        self.assertTrue(d1 == approx(d2, 1e-5))
        #dictionnaire vide
        d1 = {}
        d2 = {}
        self.assertTrue(d1 == approx(d2, 1e-5))

    def test_evaluate_dict_approx_comparison_default_tolerance(self):
        # tous approchés OK
        d1 = {"a": 0.1 + 0.2, "b": 0.1 + 0.2, "c": 0.1 + 0.2}
        d2 = {"a": 0.3, "b": 0.3, "c": 0.3}
        self.assertTrue(d1 == approx(d2))
        # aucun approché OK
        d1 = {"a": 0.1 + 0.2, "b": 0.1 + 0.2, "c": 0.1 + 0.2}
        d2 = {"a": 0.3, "b": 0.3, "c": 0.3}
        self.assertTrue(d1 == approx(d2))
        # un approché KO, au milieu
        d1 = {"a": 0.1 + 0.2, "b": 0.1 + 0.2, "c": 0.1 + 0.2}
        d2 = {"a": 0.3, "b": 0.4, "c": 0.3}
        self.assertFalse(d1 == approx(d2))
        #dictionnaire singleton
        d1 = {"a": 0.1 + 0.2}
        d2 = {"a": 0.3}
        self.assertTrue(d1 == approx(d2))
        #dictionnaire vide
        d1 = {}
        d2 = {}
        self.assertTrue(d1 == approx(d2))
       

class TestEvaluatorExpectedWithApprox(unittest.TestCase):

    def __build_module_from_source(self, source: str) -> ModuleType:
        """
        Build a module containing the functions declared in the given `source`.
        """
        from types import ModuleType
        fake_module = ModuleType(self.evaluator.get_filename())
        exec(source, fake_module.__dict__)
        return fake_module

    def setUp(self):
        self.evaluator = Evaluator(filename="<string>")
        self.mock_backend = backend_patch.start()

    def tearDown(self):
        backend_patch.stop()
        
    def test_expected_with_approx_passes(self):    
        source = \
"""
def moitie(x : float) -> float:
    '''
    $$$ moitie(5)
    approx(2.5)
    $$$ moitie(1.33333)
    approx(0.66, 1e-2)
    '''
    return x / 2
"""
        self.evaluator.set_source(source)
        self.evaluator.set_module(self.__build_module_from_source(source))
        l1doctests = self.evaluator.evaluate()
        self.assertEqual(len(l1doctests), 1)
        l1doctest = l1doctests[0]
        self.assertEqual(l1doctest.count_tests(), 2)
        self.assertEqual(l1doctest.count_passed_tests(), 2)

    def test_expected_with_approx_list_passes(self):    
        source = \
"""
def moitie_liste(l : list) -> list[float]:
    '''
    $$$ moitie_liste([5, 10, 15])
    approx([2.5, 5, 7.5])
    $$$ moitie_liste([1.33333, 2.66666, 4.0])
    approx([0.66, 1.33, 2.0], 1e-2)
    '''
    res = []
    for x in l:
        res.append(x / 2)
    return res
"""
        self.evaluator.set_source(source)
        self.evaluator.set_module(self.__build_module_from_source(source))
        l1doctests = self.evaluator.evaluate()
        self.assertEqual(len(l1doctests), 1)
        l1doctest = l1doctests[0]
        self.assertEqual(l1doctest.count_tests(), 2)
        self.assertEqual(l1doctest.count_passed_tests(), 2)

    def test_expected_with_approx_dict_passes(self):
        source = \
"""
def moitie_dict(d : dict) -> dict:
    '''
    $$$ moitie_dict({"a": 5, "b": 20, "c": 15})
    approx({"a": 2.5, "b": 10, "c": 7.5})
    $$$ moitie_dict({"a": 1.33333, "b": 2.66666, "c": 4.0})
    approx({"a": 0.66, "b": 1.33, "c": 2.0}, 1e-2)
    '''
    res = {}
    for k, v in d.items():
        res[k] = v / 2
    return res
"""
        self.evaluator.set_source(source)
        self.evaluator.set_module(self.__build_module_from_source(source))
        l1doctests = self.evaluator.evaluate()
        self.assertEqual(len(l1doctests), 1)
        l1doctest = l1doctests[0]
        self.assertEqual(l1doctest.count_tests(), 2)
        self.assertEqual(l1doctest.count_passed_tests(), 2)

    def test_expected_with_approx_tuple_passes(self):
        source = \
"""
def moitie_tuple(t : tuple) -> tuple:
    '''
    $$$ moitie_tuple((5, 10, 15))
    approx((2.5, 5, 7.5))
    $$$ moitie_tuple((1.33333, 2.66666, 4.0))
    approx((0.66, 1.33, 2.0), 1e-2)
    '''
    res = ()
    for x in t:
        res += (x / 2,)
    return res
"""
        self.evaluator.set_source(source)
        self.evaluator.set_module(self.__build_module_from_source(source))
        l1doctests = self.evaluator.evaluate()
        self.assertEqual(len(l1doctests), 1)
        l1doctest = l1doctests[0]
        self.assertEqual(l1doctest.count_tests(), 2)
        self.assertEqual(l1doctest.count_passed_tests(), 2)