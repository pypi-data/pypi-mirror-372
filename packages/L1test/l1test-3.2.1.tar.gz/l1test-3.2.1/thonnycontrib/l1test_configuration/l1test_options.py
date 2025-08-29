from tkinter import ttk
from thonny.config_ui import ConfigurationPage
from ..properties import PLUGIN_NAME
from thonny import get_workbench
from ..i18n.languages import tr
from thonny import ui_utils
import tkinter as tk

# Default config
DEFAULT_DOC_GENERATION_AFTER_RETURN = True
DEFAULT_IMPORT_MODULE_IN_SHELL = True
DEFAULT_CLOSE_FUNCTION_ROWS = False
DEFAULT_OPEN_ONLY_RED_FUNCTIONS = True
DEFAULT_HIGHLIGHT_EXCEPTIONS = False
DEFAULT_REPORT_EXCEPTION_DETAIL = True 
DEFAULT_MOVE_ERRORVIEW_TO_BOTTOM = False
DEFAULT_EVALUATE_FUNCTIONS_WITH_SAME_NAME = False
DEFAULT_DOCSTRING_PATTERN_DEF = """\"\"\" à_remplacer_par_ce_que_fait_la_fonction

Précondition : 
Exemple(s) :
$$$ 
\"\"\""""
DEFAULT_DOCSTRING_PATTERN_CLASS = """\"\"\" à_remplacer_par_ce_que_fait_la_classe

Exemple(s) :
$$$ 
\"\"\""""

# Option names
AUTO_GENERATON_DOC = "auto_generaton_doc"
IMPORT_MODULE = "import_module"
FOLD_ALL_FUNCTIONS = "close_function_rows"
EXPAND_ONLY_RED_FUNCTIONS = "open_only_red_functions"
HIGHLIGHT_EXCEPTIONS = "highlight_exceptions"
REPORT_EXCEPTION_DETAIL = "exception_detail"
MOVE_ERRORVIEW_TO_BOTTOM = "move_errorview_to_bottom"
EVALUATE_FUNCTIONS_WITH_SAME_NAME = "evaluate_functions_with_same_name"
DOCSTRING_PATTERN_DEF = "docstring_pattern_def"
DOCSTRING_PATTERN_CLASS = "docstring_pattern_class"

# Dict of options name and default value
OPTIONS = {
    AUTO_GENERATON_DOC : DEFAULT_DOC_GENERATION_AFTER_RETURN,
    IMPORT_MODULE : DEFAULT_IMPORT_MODULE_IN_SHELL,
    FOLD_ALL_FUNCTIONS: DEFAULT_CLOSE_FUNCTION_ROWS,
    EXPAND_ONLY_RED_FUNCTIONS : not DEFAULT_CLOSE_FUNCTION_ROWS,
    HIGHLIGHT_EXCEPTIONS: DEFAULT_HIGHLIGHT_EXCEPTIONS,
    REPORT_EXCEPTION_DETAIL: DEFAULT_REPORT_EXCEPTION_DETAIL,
    MOVE_ERRORVIEW_TO_BOTTOM: DEFAULT_MOVE_ERRORVIEW_TO_BOTTOM,
    EVALUATE_FUNCTIONS_WITH_SAME_NAME: DEFAULT_EVALUATE_FUNCTIONS_WITH_SAME_NAME,
    DOCSTRING_PATTERN_DEF: DEFAULT_DOCSTRING_PATTERN_DEF,
    DOCSTRING_PATTERN_CLASS : DEFAULT_DOCSTRING_PATTERN_CLASS
}

def init_options():
    """
    Initialise dans le workbench les options du plugin.
    """
    for opt in OPTIONS :
        if not get_workbench().get_option(opt) :
            get_workbench().set_default("%s." % PLUGIN_NAME + opt, OPTIONS[opt])

            
def get_option(name: str): 
    """
    Renvoie la valeur dans le workbench de l'option passée en paramètre.

    Paramètres:
    - name : le nom de l'option, tel que définie ds globals.py 
    """
    return get_workbench().get_option("%s." % PLUGIN_NAME + name)

def set_option(name, value):
    get_workbench().set_option("%s." % PLUGIN_NAME + name, value)

class L1TestConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        ConfigurationPage.__init__(self, master)
        set_option(DOCSTRING_PATTERN_DEF, get_option(DOCSTRING_PATTERN_DEF))
        
        self.add_checkbox("%s.%s" % (PLUGIN_NAME, AUTO_GENERATON_DOC), 
                          tr("Generate the docstring automatically after a line break at a function name."))

        self.add_checkbox("%s.%s" % (PLUGIN_NAME, IMPORT_MODULE), 
                          tr("Import the module executed in the shell."))
        
        self.add_checkbox("%s.%s" % (PLUGIN_NAME, FOLD_ALL_FUNCTIONS),
                          tr("Fold all function in %s view.") % PLUGIN_NAME,
                          callback=lambda: set_option(EXPAND_ONLY_RED_FUNCTIONS, not get_option(FOLD_ALL_FUNCTIONS)))
         
        self.add_checkbox("%s.%s" % (PLUGIN_NAME, EXPAND_ONLY_RED_FUNCTIONS),
                          tr("Expand only red functions in %s view.") % PLUGIN_NAME,
                          callback=lambda: set_option(FOLD_ALL_FUNCTIONS, not get_option(EXPAND_ONLY_RED_FUNCTIONS)))
        
        self.add_checkbox("%s.%s" % (PLUGIN_NAME, HIGHLIGHT_EXCEPTIONS), 
                          tr("Highlight failed tests (only those that throw an exception)."))
        
        self.add_checkbox("%s.%s" % (PLUGIN_NAME, MOVE_ERRORVIEW_TO_BOTTOM), 
                          tr("Place the error view at the bottom of the Thonny IDE (next to the `Shell` view). " + 
                             "By default, the error view is placed below the `L1Test` view. Thonny must be restarted after having modified this option."))

        self.add_checkbox("%s.%s" % (PLUGIN_NAME, EVALUATE_FUNCTIONS_WITH_SAME_NAME), 
                          tr("In case of functions with the same name: execute the code of the function and not the code Python would execute (doctest behaviour) "))

    def add_checkbox(
            self, flag_name, description, callback=None, row=None, column=0, padx=0, pady=0, columnspan=1, tooltip=None
    ):
        variable = get_workbench().get_variable(flag_name)
        checkbox = ttk.Checkbutton(self, text=description, variable=variable, command=callback)
        checkbox.grid(
            row=row, column=column, sticky=tk.W, padx=padx, pady=pady, columnspan=columnspan
        )

        if tooltip is not None:
            ui_utils.create_tooltip(checkbox, tooltip)
