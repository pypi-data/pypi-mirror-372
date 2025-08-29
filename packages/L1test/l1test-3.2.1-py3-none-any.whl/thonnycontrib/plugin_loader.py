import re
from thonny import get_workbench
from thonny.ui_utils import select_sequence
from .frontend.l1test_reporter import L1TestErrorView, L1TestTreeView
from .frontend.main_generator.main_generator import MainGenerator
from .properties import  ERROR_VIEW_LABEL, PLUGIN_NAME
from .utils import (
    assert_one_line_is_selected,
    get_focused_writable_text,
    get_selected_line, 
    get_image_path
)
from .l1test_configuration.l1test_options import *
from .frontend import get_l1test_runner
from .frontend import get_outliner
from functools import partial
from .frontend.docstring_generator import get_doc_generator
import thonnycontrib.i18n.languages as languages

def run_all_tests():
    """
    Cette fonction est invoquée quand le button `l1test` est cliqué.
    Cette fonction permet d'envoyer au l1test_backend la commande L1test.
    """
    get_l1test_runner().run_l1test()
    
      
def generate_docstring(auto: bool, event=None): 
    """
    Cette fonction est invoquée quand le button `doc_generator` est cliqué. Ou quand on 
    réalise un saut de ligne après la déclaration d'une fonction.

    Args:
        auto (bool):  Si True, alors la docstring sera générée automatiquement après un saut de ligne. 
        Sinon, la docstring sera générée quand le button `doc_generator` est cliqué.
        event (Any, optional): Si event est différent de None, alors un saut de ligne a été réalisé. 
        et donc la docstring sera générée automatiquement.
        Defaults to None.
    """
    # Ignorer les sauts à la ligne en mode manuel
    if (not auto and event != None):
        return

    if _writable_text_is_focused(): # on vérifie si la zone séléctionnée est une zone de l'éditeur
        text_widget = get_focused_writable_text()
        selected_line = get_selected_line(text_widget) 
        docGenerator = get_doc_generator(auto)  
        docGenerator.run(selected_line - 1 if auto else selected_line, text_widget)


def generate_main():
    """
    Generate the __main__ function.
    """
    text_widget = get_focused_writable_text()
    main_generator = MainGenerator(text_widget.get("1.0", "end"))
    main_generator.generate(text_widget)
    del main_generator # destruction de l'objet en mémoire (for better performance)
    

def _writable_text_is_focused():
    """
    Returns:
        boolean: Returns True if the selected zone is a writable text.
    """
    return get_focused_writable_text() is not None


## PRIVATE FUNCTIONS : constructing and configuring of the plugin ##
####################################################################

def __ensure_space_after_doc_marker():
    """
    Ensures that the L1Test docstring pattern always has a single space
    after the '$$$' marker. Without this when Thonny reads the configuration.ini where it saved the docstring, it automatically removes the space after the '$$$' marker
    """
    for key in ("docstring_pattern_def", "docstring_pattern_class"):
        option = f"L1Test.{key}"
        original = get_workbench().get_option(option)
        # Insert a space after any $$$ not already followed by one
        fixed = re.sub(r"\$\$\$(?! )", "$$$ ", original)
        if fixed != original:
            get_workbench().set_option(option, fixed)

def __init_language():
    languages.set_language(get_workbench().get_option("general.language"))

def __init_l1test_options():
    init_options()
    get_workbench().add_configuration_page(PLUGIN_NAME, PLUGIN_NAME, L1TestConfigurationPage, 30)

def __init_l1test_views():
    get_workbench().add_view(L1TestTreeView, PLUGIN_NAME, "nw", visible_by_default=True)
    get_workbench().add_view(L1TestErrorView, ERROR_VIEW_LABEL, "sw" if not get_option(MOVE_ERRORVIEW_TO_BOTTOM) else "s", visible_by_default=False)

def __init_l1test_commands():
    # Création du button l1test au niveau de la barre des commandes
    get_workbench().add_command(command_id=PLUGIN_NAME,
                                menu_name=PLUGIN_NAME,  
                                command_label=tr("Run all tests"),
                                handler=run_all_tests,
                                include_in_toolbar=True, #j'inclue ici ce bouton dans la toolbar 
                                image=get_image_path("l1test_icon.png"),
                                caption=PLUGIN_NAME)
    
    # Création du button L1Test dans la barre de menu en haut.  
    get_workbench().add_command(command_id="Run one test",
                                menu_name=PLUGIN_NAME,  
                                command_label=tr("*Run tests for..."),
                                image=get_image_path("l1test_icon.png"),
                                submenu=get_outliner().get_menu()
    )
    
    # Création du bouton dans le menu 'Edit' pour lancer la génération de docstring
    get_workbench().add_command(command_id="doc_generator",
                                menu_name="edit",  
                                command_label=tr("Generate a docstring"),
                                handler=partial(generate_docstring, auto=False), 
                                tester=_writable_text_is_focused and assert_one_line_is_selected,
    )
     
    # Création du bouton dans le menu 'Edit' pour générer le main
    get_workbench().add_command(command_id="main_generator",
                                menu_name="edit",  
                                command_label=tr("Generate a __main__"),
                                handler=generate_main, 
                                tester=_writable_text_is_focused,
                                default_sequence=select_sequence("<Alt-m>", "<Command-Alt-m>", "<Alt-m>"),
                                accelerator="Alt+m"
    )

def __add_event_binding():
    # Quand un saut de ligne est réalisé après la déclaration d'une fonction,
    # alors une docstring sera générée automatiquement.
    get_workbench().bind_class("EditorCodeViewText", 
                               "<KeyRelease-Return>", 
                               lambda event: generate_docstring(auto=get_option(AUTO_GENERATON_DOC), event=event))

def load_plugin():
    """
    load_plugin est un nom de fonction spécifique qui permet à thonny de charger les élements du plugin
    """
    # these functions should be called in this order
    __init_language()
    __init_l1test_options()
    __init_l1test_views()     
    __init_l1test_commands()
    __add_event_binding()

    __ensure_space_after_doc_marker()
