from typing import List
from .l1test_error_view import L1TestErrorView
from .l1test_treeview import L1TestTreeView
from ..properties import *
from ..l1test_configuration.l1test_options import *
from ..backend.ast_parser import L1DocTest
from thonny.codeview import *
from ..utils import format_filename_to_hyperlink, remove_url_part
import thonny

class L1TestReporter():    
    def __init__(self, main_view_class=L1TestTreeView, error_view_class=L1TestErrorView):
        self.__treeview_class = main_view_class
        self.__error_view_class = error_view_class 
        
        self._workbench = thonny.get_workbench()
        self.__treeview: L1TestTreeView = self._workbench.get_view(self.__treeview_class.__name__)
        self.__error_view: L1TestErrorView = self._workbench.get_view(self.__error_view_class.__name__)

    def display_error_msg(self, error_msg:str, title=CANNOT_RUN_TESTS_MSG, color="red"):
        """Display an error message into the `L1TestErrorView`.
        The `prefix_info` is the title preceding the error message.
        
        Args:
            error_msg (str): the error message to be displayed
            prefix_info (str, optional): the title preceding the error message. 
            Defaults to CANNOT_RUN_TESTS_MSG.
            color (str, optional): the color of the whole content. Defaults to "red".
        """
        self.__error_view.clear()
        if title:
            title = title if title.endswith("\n") else title + "\n"
            self.__error_view.append_text(title, tags=("darkred", "title"))

        hyperlink_error = format_filename_to_hyperlink(error_msg)

        if hyperlink_error: 
            self.__error_view.append_rst(hyperlink_error) # hyperlink doit être ajouté en mode RST
            error_msg = remove_url_part(error_msg) 
            self.__error_view.append_text(error_msg, tags=color) # le reste du message est ajouté en mode texte
        else:
            self.__error_view.append_text(error_msg, tags=color)
                       
    def display_tests_results(self, verdicts: List[L1DocTest]):
        """Display the verdicts into the `L1TestTreeView`.

        Args:
            verdicts (List[L1DocTest]): the dictionary of verdicts.
        """
        self.__treeview.set_l1doctests(verdicts)
        self.__treeview.update_tree_contents(verdicts)
    
    def set_treeview_class(self, treeview_class):
        self.__treeview_class = treeview_class   
    
    def get_error_view_class(self, error_view_class):
        self.__error_view_class = error_view_class      
    
    def get_treeview(self) -> L1TestTreeView:
        return self.__treeview    
    
    def get_error_view(self) -> L1TestErrorView:
        return self.__error_view    
    