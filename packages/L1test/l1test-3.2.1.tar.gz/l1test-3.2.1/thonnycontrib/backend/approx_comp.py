# fonction approx pour comparer des flottants avec une précision fournie
# très largement inspiré du approx de pytest
# https://docs.pytest.org/en/4.6.x/_modules/_pytest/python_api.html#approx
# Auteur : Mirabelle

# La fonction approx crée un objet de type ApproxXXX 
# Les objets ApproxXXX contiennent une méthode __eq__ qui prend en compte
# la tolérance passée en paramètre ou celle par défaut
# C'est ainsi que fait pytest. Ça marche car x == y est récrit en Python en
# x.__eq__(y) MAIS il semble que c'est finalement y.__eq__(x) qui est exécuté,
# peut-être quand le __eq__ de x ne sait pas répondre.
# Donc x == approx(y) exécute ApproxXXX(y).__eq__(x)
# démo :
# >>> class truc(object):
# ...    def __eq__(self, other):
# ...       print("eq truc")
# ... 
# >>> t = truc()
# >>> 1 == t
# eq truc
# >>> "ert" == t
# eq truc
# >>> [] == t
# eq truc
# >>> None == t
# eq truc

from ..i18n.languages import tr

DEFAULT_TOLERANCE = 1e-6

def are_close(x:float, y:float, tol:float) -> bool:
    """
    Compare x et y avec une tolérance tol.
    """
    return abs(x - y) <= tol

from abc import ABC, abstractmethod

class ApproxBase(ABC):
    DEFAULT_TOLERANCE = 1e-6

    def __init__(self, expected, tol=None):
        self.expected = expected
        self.tolerance = tol if tol is not None else self.DEFAULT_TOLERANCE

    def __eq__(self, actual) -> bool:
        return self.compare(actual)

    @abstractmethod
    def compare(self, actual) -> bool:
        """
        Determines whether the actual value is approximately equal to the expected value, within the specified tolerance.

        Args:
            actual: The actual value to compare with the expected value.

        Returns:
            True if the actual value is approximately equal to the expected value, within the specified tolerance. False otherwise.
        """
        pass

    def __repr__(self):
        return "{} +- {}".format(self.expected, self.tolerance)


class ApproxSimple(ApproxBase):

    def compare(self, actual) -> bool:
        return are_close(self.expected, actual, self.tolerance)


class ApproxList(ApproxBase):

    def compare(self, actual) -> bool:
        if len(self.expected) != len(actual):
            return False
        return all(are_close(e, a, self.tolerance) for e, a in zip(self.expected, actual))


class ApproxDict(ApproxBase):

    def compare(self, actual) -> bool:
        if (len(self.expected) != len(actual)) or (set(self.expected.keys()) != set(actual.keys())):
            return False
        return all(are_close(self.expected[k], actual[k], self.tolerance) for k in self.expected.keys())


class ApproxTuple(ApproxBase):

    def compare(self, actual) -> bool:
        if len(self.expected) != len(actual):
            return False
        return all(are_close(e, a, self.tolerance) for e, a in zip(self.expected, actual))
        
        
def approx(expected, tol=None) -> ApproxBase:
    """
    Renvoie un objet qui saura comparer expected avec
    une autre valeur (par __eq__) éventuellement avec une tolérance
    tol.
    """
    if tol and tol<0:
        raise ValueError("La tolérance doit être positive ou nulle : {}".format(tol))
    if isinstance(expected, float) or isinstance(expected, int):
        return ApproxSimple(expected, tol)
    if isinstance(expected, list):
        if all((isinstance(x, int) or isinstance(x, float)) for x in expected): 
            return ApproxList(expected, tol)
    if isinstance(expected, dict):
        if all((isinstance(x, int) or isinstance(x, float)) for x in expected.values()): 
            return ApproxDict(expected, tol)
    if isinstance(expected,tuple):
        if all((isinstance(x, int) or isinstance(x, float)) for x in expected):
            return ApproxTuple(expected, tol)
    raise TypeError("approx ne s'applique pas au type" + f" {type(expected).__name__}")
