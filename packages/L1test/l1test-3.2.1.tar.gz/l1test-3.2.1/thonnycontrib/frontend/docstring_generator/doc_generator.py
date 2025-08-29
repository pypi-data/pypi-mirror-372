from .doc_template import *
from thonnycontrib.properties import CANNOT_GENERATE_THE_DOCSTRING
from thonnycontrib.frontend import get_l1test_runner
from thonnycontrib.exceptions import DocGeneratorParserException, FrontendException, NoFunctionSelectedToDocumentException
from thonnycontrib.utils import replace_error_line, get_last_exception
from thonnycontrib.ThonnyLogsGenerator import log_doc_in_thonny
import thonnycontrib.frontend.docstring_generator as docstring_generator

from typing import List
from thonny.tktextext import *  
from thonny.editors import EditorCodeViewText
from thonny import get_workbench
import re, sys, textwrap

r""" Docstring Generator Module
Description:
------------
This module generates a docstring using the templates.

For a selected line the `DocGenerator` tries to verify if the selected line
corresponds to a function signature. If the selected line is a function 
signature so a the `DocGenerator` will build a custom function with the given
selected line and then it parses(with AST parser) this function. If the AST parser
fails so the error will be displayed in the ErrorView. otherwise, the docstring
will be generated.

About templates, the docstring generator invokes the `DefaultDocTemplate` by default. 
The `DocTemplate.DefaultDocTemplate` class contains an implementation 
of a default template. 

How to use the Generator in thonny IDE:
---------------------------------------
- Right click on a function or a class and choose in the `edit menu` ~Generate Docstring~ 
button. You can also click on the body of the function to generate the docstring.

- Just a return on a function declaration will generate its docstring. The declaration
should be finished by a ":" caractere.
"""

class DocParser:
    def __init__(self, filename="", source=""):
        self._filename = filename
        self._source = source
    
    def parse_source(self, error_line:int=None):
        """
        Parses the given `source` and returns a list of 
        AST nodes that may contains a doctsring.
        
        As the AST python module stated in its documentation, the AST nodes that can 
        contain a dosctring are reported at ~SourceParser.SUPPORTED_TYPES~.
        
        Args:
            error_line(int): Set it only if you want to change the error line in 
            the raised exception. If `None`, so the error line mentioned in the error will 
            be kept. 
        
        Raises:
            DocGeneratorParserException: if the ast parser is failed.
        """
        try :
            parsed = ast.parse(self._source, self._filename, mode="single").body
            return parsed[0] if len(parsed) == 1 else None
        except Exception as e: # if a compilation error occurs during the parsing
            error_info = sys.exc_info()
            last_exception = get_last_exception(error_info)
            if error_line:
                last_exception = replace_error_line(last_exception, error_line)
            raise DocGeneratorParserException(last_exception)    
    
    def get_filename(self):
        return self._filename
    
    def set_filename(self, filename: str):
        self._filename = filename
    
    def set_source(self, source: str):
        self._source = source
        
    def get_source(self):
        return self._source 
    
    def set_ast_parser(self, parser) :
        self._ast_parser = parser

class DocGenerationStrategy(ABC):
    _SIGNATURE_REGEX = r"\s*(?P<id>def|class)\s*.*\s*:\s*$"
    
    def __init__(self, text_widget:EditorCodeViewText, parser:DocParser=DocParser()):
        self._parser = parser 
        self._text_widget = text_widget
    
    @abstractmethod
    def can_generate(self, selected_lineno:int) -> bool:
        pass
    
    @abstractmethod
    def generate(self) -> None:
        pass
    
    def _generate(self, signature:str, selected_lineno:int=None) -> str:   
        """Generate a docstring from a given signature (or prototype).
        
        Args:
            - signature(str): The signature for which the docstring will be generated.
            The signature should always be finished by a ":" caractere, otherwise the 
            docstring not will be generated. 
            - selected_lineno(int, Optional): This parameter is optional. It is the line number
            of the signature. This will be usefull for errors raised by the AST parser.
            If the ast parser raises an exception, the line number of the exception will be set to
            the given lineno.
            - text_widget(EditorCodeViewText, Optional): The view in which the generated docstring will 
            be inserted. Set to `None` if you want just to get the generated docstring. If `None` the
            generated docstring will not be inserted in any widget.
        
        Return:
            str: returns the generated docstring.
        
        Raises:
            - NoFunctionSelectedToDocument: When a selected line don't corresponds to 
            a function declaration. 
            - DocGeneratorParserException: when the ast parser fails.
        """
        if signature is None: signature = ""
        
        # We should check that the line is a function declaration and that ends with ':' character. 
        declaration_match = re.match(self._SIGNATURE_REGEX, signature)

        if not declaration_match:
            raise NoFunctionSelectedToDocumentException()
        else:               
            template:DocTemplate = DocTemplateFactory.create_template(declaration_match.group("id")) 
            
            generated_temp = self.__get_generated_template(template, signature, selected_lineno)
            
            indent = self.__compute_indent(signature)
            generated_doc = textwrap.indent(generated_temp, indent)
            if self._text_widget:
                doc_start_line = selected_lineno + 1
                doc_end_line = doc_start_line + generated_doc.count("\n") - 1
                self._text_widget.insert(f"{doc_start_line}.0", generated_doc)
                self._text_widget.see(f"{doc_start_line}.0")

                self.highlight_generated_docstring(doc_start_line, doc_end_line)
            return generated_doc
    
    @abstractmethod
    def highlight_generated_docstring(self, doc_start_line:int, doc_end_line:int):
        pass    
    
    def __get_generated_template(self, template:DocTemplate, signature:str, selected_lineno:int) -> str:
        """
        Creates a custom function with the given `signature` then parses this function and if the
        AST parser success so the docstring will be generated. If the AST parser fails, so the 
        reported exception will be raised.

        Args:
            signature (str): the signature for which the docstring will be generated.
            selected_lineno (int): the line that corresponds to the selected line. This arg is used 
            to change the error line in the reported exception to the given `selected_line`. Remember
            that the error line will be always "1" if the ast parser fails, because the parsed source
            contains only the custom function.
            
        Returns:
            (str): The generated template.
            
        Raises: 
            DocGeneratorParserException: when the ast parser fails.
        """
        # The approach is to take the signature of the selected function then
        # adds a custom body to this function.
        custom_func = self._create_custom_body(signature)
        
        # don't forgot that the result of parsing is a list of supported nodes
        # -> see the doc
        self._parser.set_source(custom_func)
        node = self._parser.parse_source(selected_lineno)
        
        # Generate an event in Thonny with l1test/ThonnyLogsGenerator.log_doc_in_thonny
        log_doc_in_thonny((selected_lineno, self._parser.get_filename(), self._parser.get_source()))
        
        return template.get_template(node)

    def __compute_indent(self, signature:str) -> int:
        """
        Get the indentation based on the whitespaces located in the given `signature`.

        Args:
            signature (str): a signature of a function

        Returns:
            int: returns the indentation based on the whitespaces located in the given `signature`.
        """
        space_match = re.search("^(\s+)", signature)
        python_indent = 4
        sig_indent = len(space_match.group(1)) if space_match else 0
        return " " * (sig_indent + python_indent)
    
    def _create_custom_body(self, signature:str):
        signature = signature.strip()
        indent = " " * 4
        return signature + "\n" + indent + "pass"
    
    def set_parser(self, parser: DocParser):
        self._parser = parser
        
    def get_parser(self):
        return self._parser
    
    def set_filename(self, filename):
        self._parser.set_filename(filename)
        
    def set_text_widget(self, text_widget:EditorCodeViewText):
        self._text_widget = text_widget
    
class AutoGenerationStrategy(DocGenerationStrategy):
    def __init__(self, text_widget:EditorCodeViewText=None, parser=DocParser()):
        super().__init__(text_widget, parser)
        self.__selected_sig = None
        self.__selected_lineno = None
    
    def can_generate(self, selected_lineno:int) -> bool:
        line_content = self._text_widget.get(str(selected_lineno)+".0", str(selected_lineno+1)+".0")
        if line_content.strip().strip("\n") != "":
            self.__selected_sig = line_content
            self.__selected_lineno = selected_lineno
        return self.__selected_sig != ""
    
    def generate(self):
        return super()._generate(self.__selected_sig, self.__selected_lineno)
    
    def highlight_generated_docstring(self, doc_start_line:int, doc_end_line:int):
        pass
        
class ManualGenerationStrategy(DocGenerationStrategy):
    _OUTLINER_REGEX = r"\s*(?P<type>def|class)[ ]+(?P<name>[\w]+)"
    
    def __init__(self, text_widget:EditorCodeViewText=None, parser=DocParser()):
        super().__init__(text_widget, parser)
        self.__nodes: List[SourceNode] = []
        self.__selected_node = None
    
    def can_generate(self, selected_lineno:int) -> bool:
        self.__nodes = self.__parse(self._text_widget.get("1.0", "end"))
        self.__selected_node = next((node for node in self.__nodes if node.get_starting_lineno() <= selected_lineno <= node.get_ending_lineno()), None)
        return self.__selected_node is not None
    
    def generate(self) -> str:
        return super()._generate(self.__selected_node.get_signature(), self.__selected_node.get_starting_lineno())
    
    def highlight_generated_docstring(self, doc_start_line:int, doc_end_line:int):
        self._text_widget.select_lines(doc_start_line, doc_end_line) # highlight the lines
        get_workbench().after(600, lambda: self._text_widget.select_lines(0,0)) # remove highlighting the lines after 600ms
    
    def __parse(self, source: str):
        current_node = None
        lines = source.splitlines()
        lineno = 1
        last_non_empty_line = None
        current_indentation = None

        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                lineno += 1
                continue

            indentation = len(line) - len(stripped_line)
            match = re.match(self._OUTLINER_REGEX, line)
            
            if match:
                if current_node:
                    current_node.set_ending_lineno(last_non_empty_line or current_node.get_starting_lineno())
                    yield current_node

                current_node = SourceNode(line, lineno, None)
                current_indentation = indentation
                last_non_empty_line = None
                
            elif current_node and indentation <= current_indentation:
                # We found a line that is indented less than or equal to the current node,
                # so this line is outside of the current node's body.
                current_node.set_ending_lineno(last_non_empty_line or (lineno - 1))
                yield current_node
                current_node = None  # Reset current node since we've finished it
                
            elif stripped_line:
                last_non_empty_line = lineno

            lineno += 1

        # If there's a current_node left, we have to set its ending line number.
        if current_node:
            current_node.set_ending_lineno(last_non_empty_line or current_node.get_starting_lineno())
            yield current_node
    
    def get_nodes(self):
        return self.__nodes
        
class SourceNode():
    """
    This class represents an outlined node. An outlined node is either a class or a function.
    """ 
    def __init__(self, signature:str, starting_lineno:int, ending_lineno) -> None:
        self.__signature = signature
        self.__starting_lineno = starting_lineno
        self.__ending_lineno = ending_lineno
        
    def get_starting_lineno(self):
        return self.__starting_lineno  
    
    def get_ending_lineno(self):
        return self.__ending_lineno
    
    def set_ending_lineno(self, ending_lineno):
        self.__ending_lineno = ending_lineno
        
    def set_signature(self, signature):
        self.__signature = signature
    
    def get_signature(self):
        return self.__signature
    
    def __str__(self) -> str:
        return f"signature: {self.__signature}, s_lineno: {self.__starting_lineno}, e_lineno: {self.__ending_lineno}" 
    
    
class DocGenerator():
    def __init__(self, strategy:DocGenerationStrategy=AutoGenerationStrategy()):
        docstring_generator._doc_generator = self
        self._has_exception = False 
        self._strategy = strategy
   
    def run(self, selected_lineno:int, text_widget:EditorCodeViewText):
        try:
            self.__run(selected_lineno, text_widget)
        except NoFunctionSelectedToDocumentException as e:
            pass # do nothing
        except FrontendException as e: # parsing error
            self.set_has_exception(True)
            self._show_error(str(e))

    def __run(self, selected_lineno:int, text_widget:EditorCodeViewText):
        self._strategy.set_text_widget(text_widget)
        if self._strategy.can_generate(selected_lineno):
            filename = get_workbench().get_editor_notebook().get_current_editor().get_filename()
            if not filename:
                filename = "<unknown>" 
                    
            self._strategy.set_filename(filename)
            self._strategy.generate()   
            
            # après la génération (réussie) on vérifie si docgen avait rencontré une exception avant. Si oui, 
            # on supprime l'exception de docgen (car elle a été déja montrée).
            if get_l1test_runner().has_exception() or self.has_exception(): # si docgen avait lancé une exception avant
                # si les deux ont lancé une exception, on supprime l'exception de docgen car elle a été déja montrée
                if get_l1test_runner().has_exception() and self.has_exception(): 
                    get_l1test_runner().clean_error_view()
                    get_l1test_runner().get_reporter().get_error_view().hide_view()
                    get_l1test_runner().get_reporter().get_treeview().show_view()
                elif get_l1test_runner().has_exception(): # si docgen n'avait pas lancé d'exception
                    pass # on s'en fout car l'exception concerne l1test et non pas docgen
                else:
                    self._show_treeview()
                
                self.set_has_exception(False) # success
    
    def _show_treeview(self):
        """
        Cleans the ErrorView and hides it. Retreives the Treeview and shows it.
        """
        get_l1test_runner().hide_errorview_and_show_treeview()
    
    def _show_error(self, error_msg:str, error_title:str=CANNOT_GENERATE_THE_DOCSTRING):
        """
        Shows the error in the ErrorView if the docstring generator raises an exception.
        """
        l1test_runner = get_l1test_runner()
        if self.has_exception():
            l1test_runner.show_errors(exception_msg=error_msg, title=error_title)
            l1test_runner.get_reporter().get_error_view().show_view() 
            l1test_runner.get_reporter().get_treeview().hide_view()     
        
    def has_exception(self):
        return self._has_exception
    
    def set_has_exception(self, has_exception: bool):
        self._has_exception = has_exception
        
    def get_strategy(self):
        return self._strategy
    
    def set_strategy(self, strategy: DocGenerationStrategy):
        self._strategy = strategy
