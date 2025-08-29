from typing import List
import re
from thonny import get_workbench
from functools import partial
from ..properties import PLUGIN_NAME
import tkinter as tk
from ..utils import  get_photoImage 
from thonnycontrib import frontend 

_OUTLINER_REGEX = r"\s*(?P<type>def|class)[ ]+(?P<name>[\w]+)"

class OutlinedNode():
    """
    This class represents an outlined node. An outlined node is either a class or a function.
    """ 
    def __init__(self, type:str, name:str, lineno:int) -> None:
        self.__type = type
        self.__name = name
        self.__lineno = lineno
        self.__image = get_photoImage("outline_class.png" if self.__type == "class" else "outline_method.gif")
    
    def get_type(self):
        return self.__type  
    
    def get_name(self):
        return self.__name  
    
    def get_lineno(self):
        return self.__lineno  
    
    def get_image(self):
        return self.__image 
    
    def __str__(self) -> str:
        return "{type: %s, name: %s, line: %s" % (self.__type, self.__name, self.__lineno)   

class L1TestOutliner():   
    """
    This class is responsible for parsing the source code and building the menu which contains
    the outlined nodes (classes and functions). 
    
    The parsing is done using a regular expression. 
    No AST is used, because the parsing is done on the fly, when the user clicks on the menu.
    
    The regular expression is defined in the global variable `_OUTLINER_REGEX`.
    """
    def __init__(self) -> None:
        frontend._outliner = self # singleton        
        get_workbench()._init_menu()
        # create the menu with a postcommand which will be called every time the menu is clicked
        self.menu = tk.Menu(get_workbench().get_menu(PLUGIN_NAME), postcommand=self.update_menu)
      
    def __parse(self, source:str) -> List[OutlinedNode]:
        """
        Parses a source and returns a list of the outlined nodes. 
        The outlined nodes are either a class or a function. For 
        each outlined node an object of type `OutlinedNode` is built 
        in which we store the type (class/function), the name and the lineno
        of the outlined node.
        """
        lineno = 0
        for line in source.splitlines():
            lineno += 1
            match = re.match(_OUTLINER_REGEX, line) 
            if match:
                yield OutlinedNode(match.group("type"), match.group("name"), lineno)
    
    def from_source_post_menu(self, source):
        self.clear_menu()
        for outlined in self.__parse(source):
            label = "%s %s" % (outlined.get_type(), outlined.get_name())
            image = outlined.get_image()
            self.menu.add_command(label=label, 
                                  image=image,
                                  command=partial(run_tests_for_outlined_node, outlined.get_lineno()),
                                  activebackground="white",
                                  activeforeground="darkblue",
                                  compound=tk.LEFT)
            # should save a reference to the image otherwise it will be garbage collected
            setattr(self, image.name, image)  

    def update_menu(self):
        editor = get_workbench().get_editor_notebook().get_current_editor()
        if not editor:
            self.clear_menu()
            return
        source = editor.get_code_view().get_content()
        self.from_source_post_menu(source)
    
    def clear_menu(self):
        self.menu.delete(0, tk.END)
        
    def get_menu(self):
        return self.menu

def run_tests_for_outlined_node(lineno:int):
    """
    Cette fonction est invoquée quand un item (méthode) du menu `Run test for ...` est cliqué.
    Cette fonction permet d'envoyer au l1test_backend la commande L1test avec en argument
    is_selected=True.
    """
    from thonnycontrib.frontend import get_l1test_runner
    get_l1test_runner().run_l1test(selected_line=lineno)