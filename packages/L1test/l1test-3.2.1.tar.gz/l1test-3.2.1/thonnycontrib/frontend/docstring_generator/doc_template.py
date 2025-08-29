from abc import *
import ast
from typing import List
from ...properties import PLUGIN_NAME
from ...l1test_configuration.l1test_options import DOCSTRING_PATTERN_CLASS, DOCSTRING_PATTERN_DEF, get_option

class DocTemplate(ABC):

    @abstractmethod
    def get_template(self, node:ast.AST=None) -> str:
        """Build the complete docstring template. 
        This method must invoke the above abstract methods.
        
        Args:
            node (ast.AST): The AST node in which the dosctring will be generated.

        Returns:
            str: Returns the template representation. 
        """
        pass  
    
    @abstractmethod
    def get_id_signature(self) -> str: 
        pass      
    
class DocFunctionTemplate(DocTemplate):
    '''Modifié pour coller au cours de PROG, portail MI, avec volonté
    d'alléger les docstring au max : uniquement la première phrase, la
    precond et les tests (les étudiant·es étant obligés d'indiquer des
    annotations de type).

    '''
    RETURN_LABEL = "Valeur de retour " 
    RETURN_TYPE_LABEL = "(%s) :" #"__type de retour ?__ (%s)%s"

    # I did not find how to add a final \n after patterns in
    # configuration.ini, so the default pattern is not endend
    # by a \n, which is added here.
    def get_template(self, node: ast.AST):
        return get_option(DOCSTRING_PATTERN_DEF)+'\n'
    
    def get_id_signature(self): 
        return "def" 

class DocClassTemplate(DocTemplate): 
            
    def get_template(self, node):
        return get_option(DOCSTRING_PATTERN_CLASS)+'\n'

    def get_id_signature(self): 
        return "class" 

class DocTemplateFactory:            
    @staticmethod
    def create_template(type:str):
        return DocTemplateFactory.__search_type(type)
    
    @staticmethod
    def __docTemplate_subclasses(cls=DocTemplate):
        return set(cls.__subclasses__()) \
               .union([s for c in cls.__subclasses__() \
                            for s in DocTemplateFactory.__docTemplate_subclasses(c)])
    
    @staticmethod
    def __search_type(type:str) -> DocTemplate|None:
        template_types = DocTemplateFactory.__docTemplate_subclasses()
        
        find_type = [t() for t in template_types if type==t().get_id_signature()]
        return find_type[0] if find_type else None   
