import ast
from enum import Enum
from functools import cache
from .verdicts.ExceptionVerdict import ExceptionVerdict
from .verdicts.FailedVerdict import FailedVerdict
from .verdicts.ExampleVerdict import ExampleVerdict
from ..properties import PENDING_STATE
from ..utils import create_node_representation, send_current_state
from .doctest_parser import DocTestParser, Example
from typing import List, Tuple

# Only these types can have a docstring 
# according to ast's module documentation
SUPPORTED_TYPES = (ast.FunctionDef, 
                   ast.ClassDef, 
                   ast.Module)

class L1DocTestFlag(Enum):
    """This enum represents the flag of an L1DocTest. A flag is an integer that 
    represents the global verdict of the L1DocTest. 
    
    The flag can be one of the following: `FAILED_FLAG`, `EMPTY_FLAG`, `PASSED_FLAG`.
    """
    FAILED_FLAG = -1
    EMPTY_FLAG = 0
    PASSED_FLAG = 1
    
    def from_value(value: int):
        """This method returns the flag corresponding to the given value."""
        if value not in [-1, 0, 1]:
            raise ValueError("The value must be one of the following: -1, 0, 1")
        if value == -1:
            return L1DocTestFlag.FAILED_FLAG
        elif value == 0:
            return L1DocTestFlag.EMPTY_FLAG
        else:
            return L1DocTestFlag.PASSED_FLAG
    
    def get_image_basename(self):
        """This method returns the icon corresponding to the flag."""
        if self.value == -1:
            return "failed.png"
        elif self.value == 0:
            return "warning.png"
        else:
            return "passed.png"
    
    def get_color(self):
        """This method returns the color corresponding to the flag."""
        if self.value == -1:
            return "red"
        elif self.value == 0:
            return "orange"
        else:
            return "green"
        
    def short_name(self):
        """This method returns the text corresponding to the flag."""
        if self.value == -1:
            return "Failed"
        elif self.value == 0:
            return "Empty"
        else:
            return "Passed"
    
    @staticmethod
    def get_priorities():
        return [L1DocTestFlag.FAILED_FLAG, L1DocTestFlag.PASSED_FLAG, L1DocTestFlag.EMPTY_FLAG]
    
    def is_failing(self):
        """
        Return True if the flag is `FAILED_FLAG`. Otherwise, returns False.
        """
        return self.value == -1 
    
    
class L1DocTest():
    """
    An `L1DocTest` is associated to an ast node and that groups its tests 
    containing in the docstring of that node. A `L1DocTest` handles a list of 
    the examples of type `Example`. 
    
    When a `L1DocTest` is created by the `L1TestAstParser` it is not evaluated. 
    Its global verdict (see `get_flag()`) will be `None` until it's evaluated. 
    Its `Example` are not evaluated too and thier verdicts are setted as `None`. 
    To evaluate a `L1DocTest` you should call the `evaluate()` method. Then all 
    the examples will be evaluated and the global verdict of the l1doctest will 
    be setted.
    
    Args:
        filename (str): The name of the file in which the L1Doctest is extracted.
        This is useful to know the context of the L1Doctest.
        name (str):  The name of the ast node which is associated to the L1Doctest.
        type (str): The type of the ast node which is associated to the L1Doctest. 
        related to one value reported in `SUPPORTED_TYPES` constant.
        node_lineno (int): The line of the associated ast node.
        start_lineno (int): the starting lineno of the docstring.
        Defaults to -1 If no docstring was found.
        end_lineno (int): the ending lineno of the docstring.
        Defaults to -1 If no docstring was found.
    """
    def __init__(self, filename:str, name:str, type:str, node_lineno:int, start_lineno=-1, end_lineno=-1, source_code: str = "") -> None:
        self.__filename = filename
        self.__name = name
        self.__type = type
        self.__node_lineno = node_lineno
        self.__start_lineno = start_lineno
        self.__end_lineno = end_lineno
        self.__examples:List[Example] = []
        self.__flag: L1DocTestFlag = None  # The global verdict of the l1doctest. 
                                           # Set as None while the l1doctest is not evaluated.
        self.__source_code = source_code
    
    def evaluate(self, globs:dict):
        """
        Evaluate the examples of this L1Doctest. Each example is evaluated and its 
        verdict is setted. The global verdict of the L1Doctest is also setted and you
        could access it by calling the method L1Doctest.get_flag().
        
        Args:
            globs (dict): The globals of the module in wich the L1Doctest is defined.
        Returns:
            L1DocTestFlag: The global verdict of the L1Doctest.
        """
        for example in self.get_examples(): 
            send_current_state(state=PENDING_STATE, lineno=example.lineno)
            example.compute_and_set_verdict(globs) 
        self.__flag = self.__get_global_flag() # set the global verdict of the l1doctest 
        return self.__flag
        
    def __get_global_flag(self) -> L1DocTestFlag:
        """
        This method should be invoked after the evaluation (evaluate_examples() method) 
        of the l1doctest. It returns a flag that represents the global verdict of the L1Doctest.
        
        Returns:
            L1DocTestFlag: returns a flag that represents the global 
            verdict of the l1doctest. 
        """
        assert all(ex.is_evaluated() for ex in self.__examples) # assure that all the examples are evaluated
        if not self.has_examples():
            return L1DocTestFlag.EMPTY_FLAG
        elif self.has_only_setUps() and all([ex.get_verdict().isSuccess() for ex in self.__examples]):
            return L1DocTestFlag.EMPTY_FLAG
        elif all([ex.get_verdict().isSuccess() for ex in self.__examples]):
            return L1DocTestFlag.PASSED_FLAG
        else:
            return L1DocTestFlag.FAILED_FLAG
    
    ## Stats methods ##
    def count_tests(self):
        """
        Count the number of the tests containing in this L1doctest. The setups
        are not considered in the counting.
        
        Returns:
            int: the number of the tests containing in the l1doctest.
        """ 
        return len(self.get_test_examples()) 
    
    def count_setups(self):
        """
        Count the number of the setups containing in this L1doctest. The tests
        are not considered in the counting.
        
        Returns:
            int: the number of the setups containing in the l1doctest.
        """ 
        return len(self.get_setup_examples())
    
    def count_passed_tests(self):
        """Count the number of passed tests. Return `None` if the L1Doctest is not evaluated."""
        if not self.is_evaluated():
            return None
        return sum([1 for ex in self.__examples if ex.is_a_test() and ex.get_verdict().isSuccess()])
    
    def count_failed_tests(self):
        """Count the number of failed tests. Return `None` if the L1Doctest is not evaluated."""
        if not self.is_evaluated():
            return None
        return sum([1 for ex in self.__examples if not ex.get_verdict().isSuccess() and isinstance(ex.get_verdict(), FailedVerdict)])
    
    def count_error_tests(self):
        """
        Count the number of tests that raised an exception.
        Return `None` if the L1Doctest is not evaluated
        """
        if not self.is_evaluated():
            return None
        return sum([1 for ex in self.__examples if not ex.get_verdict().isSuccess() and isinstance(ex.get_verdict(), ExceptionVerdict)])
    
    ## Sorting/filtering methods ##
    def sort_examples_by_verdicts(self, key: Tuple[ExampleVerdict, ...], reverse=True):
        """
        Sort the examples of this L1Doctest by the given key. The key is a tuple of `ExampleVerdict`.
        This method set the examples of this L1Doctest as the sorted examples.
        """
        sorted_example = sorted(self.get_examples(), key=lambda x: isinstance(x.get_verdict(), key), reverse=reverse)
        self.set_examples(sorted_example)
    
    def filter_examples_by_verdicts(self, key: Tuple[ExampleVerdict, ...]):
        """Filter the examples of this L1Doctest by the given key. The key is a tuple of `ExampleVerdict`.
        Return a list of examples that match the given key.
        """
        return [example for example in self.__examples if example.get_verdict().__class__ in key]
    
    ## Check methods ##
    def is_evaluated(self):
        """Returns True if the L1Doctest is evaluated. Otherwise, returns False."""
        return bool(self.__flag)
    
    def has_examples(self):
        """
        Returns:
            bool: Returns True if this `L1Doctest` contains at least one `Example`. 
            Otherwise, returns False.
        """
        return len(self.__examples) > 0
    
    def has_only_tests(self):
        """ 
        Return True if this L1Doctest contains only tests. Otherwise, returns False.
        """
        return self.count_tests() > 0 and self.count_tests() == len(self.__examples)
    
    def has_only_setUps(self):
        """
        Return True if this L1Doctest contains only setups. Otherwise, returns False.
        """
        return self.count_setups() > 0 and self.count_setups() == len(self.__examples)
    
    ## Add and remove methods ##
    def add_example(self, example:Example):
        """
        Add an example to the L1Doctest.

        Args:
            example (Example): The example to add.
        """
        self.__examples.append(example)
        
    def remove_example(self, example:Example):
        """
        Remove an example from the L1Doctest.

        Args:
            example (Example): The example to remove.
        """
        self.__examples.remove(example)
    
    ## Utils methods ##
    def get_test_examples(self):
        """
        Return a list of the tests of this L1Doctest.
        """
        return [ex for ex in self.__examples if ex.is_a_test()]
    
    def get_setup_examples(self):
        """
        Return a list of the setups of this L1Doctest.
        """
        return [ex for ex in self.__examples if not ex.is_a_test()]
    
    def get_verdict_from_example(self, example:Example) -> ExampleVerdict:
        """
        Return the verdict of the given example. Return None if the example is not found.
        """
        found_example = self.__get_example(example.lineno)
        return found_example.get_verdict() if found_example else None
    
    def __get_example(self, lineno:int) -> Example:
        """
        Return the example that has the given lineno. 
        Return None if the example is not found.
        """
        found = [ex for ex in self.__examples if ex.lineno == lineno]
        return found[0] if found else None

    ## Getters and Setters ##
    def get_filename(self):
        return self.__filename
    
    def get_node_lineno(self):
        """Return the line number of the node of the L1Doctest. 
        The node is the function or the class associated to the L1Doctest. """
        return self.__node_lineno
    
    def get_examples(self):
        return self.__examples
    
    def set_examples(self, examples:List[Example]):
        self.__examples = examples
    
    def get_name(self):
        """Return the name of the L1Doctest. The name is the name of the function or the class."""
        return self.__name
    
    def get_start_end_lineno(self) -> Tuple[int, int]:
        """Return the start and the end line number of the docstring of the L1Doctest."""
        return (self.__start_lineno, self.__end_lineno)

    def get_start_lineno(self):
        """Return the start line number of the docstring of the L1Doctest.""" 
        return self.__start_lineno
    
    def set_start_lineno(self, start_lineno):
        self.__start_lineno = start_lineno
    
    def get_end_lineno(self):
        """Return the end line number of the docstring of the L1Doctest."""
        return self.__end_lineno
    
    def set_end_lineno(self, end_lineno):
        self.__end_lineno = end_lineno
        
    def get_flag(self):
        """Return the flag of the L1Doctest. The flag is the global verdict of the L1Doctest."""
        return self.__flag
    
    def get_type(self):
        """Return the type of the L1Doctest. The type is the type of the node of the L1Doctest."""
        return self.__type
    
    def set_type(self, type):
        self.__type = type

    def get_source_code(self):
        return self.__source_code


## The L1DocTestParser class 
class L1TestAstParser(): 
    """
    The L1DocTestParser is responsible for parsing the source and extracts the L1DocTests.
    The main method is `parse()` that returns a generator of L1DocTests. The generator 
    yields all the L1DocTests found in the source. 
    
    Note: generators are used to avoid to load all the L1DocTests in memory. This
    is useful when the source is big. The L1DocTests are yielded one by one while parsing.
    Finally, the use of generators allows better performances and less memory consumption.
    
    The `L1DocTestParser`doesn't evaluate the created L1Doctests. Each yielded L1DocTest
    is initially unevaluated. It's the responsibility of the `Evaluator` to evaluate each 
    received L1DocTest.
    
    Example of use:
    >>> parser = L1DocTestParser("source", "filename.py")
    >>> generator = parser.parse() # returns a generator of L1DocTests
    """
    
    DOCTEST_PARSER = DocTestParser()
    
    def __init__(self, filename:str="", source:str="", mode="exec") -> None:
        self._filename = filename
        self._source = source
        self._mode = mode

    def parse(self, lineno:int=None):
        """
        Parse the source and yields all the l1doctest.
        If the line number is not None, only the l1doctest that has 
        the given line number is yielded.
        
        Args:
            lineno (int): the line number of the l1doctest to yield. If None, 
            all the l1doctests are yielded.
        Returns:
            generator: a generator of l1doctests.
        
        Raises: 
            Error: A compilation error raised by the AST module.
        """
        body = self.__get_ast_body(self._source)
        yield from self.__recursive_walking(body, lineno)
    
    def __get_ast_body(self, source) -> List[ast.AST]:
        """
        Returns the body(list of nodes) of the root node of the AST tree.
        
        Raises: 
            Error: A compilation error raised by the AST module.
        """
        return ast.parse(source, self._filename, mode=self._mode).body
    
    def __recursive_walking(self, list_nodes: list, lineno: int = None):
        """
        Search all the supported nodes in the AST tree. Even sub-nodes are visited.
        This is a recursive function, so all the visited nodes are added in the ~all_nodes~
        parameter.
        """
        for node in list_nodes:
            if isinstance(node, SUPPORTED_TYPES):
                start_line = node.lineno - 1  # ast utilise une indexation 1-based
                end_line = node.end_lineno
                source_lines = self._source.split('\n')[start_line:end_line]
                source_code = '\n'.join(source_lines)
                type = node.__class__.__name__
                l1doctest = L1DocTest(
                    self._filename, 
                    create_node_representation(node), 
                    type, 
                    node.lineno,
                    source_code=source_code
                )
                if node.body:
                    first_stmt = node.body[0]
                    if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Str):
                        l1doctest.set_start_lineno(first_stmt.lineno)
                        l1doctest.set_end_lineno(first_stmt.end_lineno)

                docstring = ast.get_docstring(node, False) or ""
                parsed_doc = self.DOCTEST_PARSER.parse(docstring, name=self._filename)

                l1doctest.set_examples(self.__filter_example_instances(l1doctest, parsed_doc))
                # Check if the current node matches the given lineno
                if lineno is None or (l1doctest.get_node_lineno() == lineno):
                    yield l1doctest

                yield from self.__recursive_walking(ast.iter_child_nodes(node), lineno)

    def __filter_example_instances(self, l1_doctest:L1DocTest, parsed_doc:list) -> List[Example]:
        """
        The filter can return an empty list if there's no example 
        in the parsed docstring. Otherwise, it will return a list of the `Example` instances 
        matching the given l1doctest.
        """
        examples = []
        for test in parsed_doc:
            if isinstance(test, Example):
                test.lineno = test.lineno + l1_doctest.get_start_lineno() - 1
                examples.append(test)
        return examples    
        
    def get_filename(self):
        return self._filename
    
    def set_filename(self, filename: str):
        self._filename = filename
    
    def get_source(self):
        return self._source
    
    def set_source(self, source: str):
        self._source = source
        
    def get_mode(self):
        return self._mode
    
    def set_mode(self, mode):
        self._mode = mode
