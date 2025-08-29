import os
from types import ModuleType

from .test_finder import FindSelectedL1DoctestStrategy
from ..exceptions import BackendException
from ..environement_vars import *
from .evaluator import Evaluator 
from thonny.common import ToplevelCommand, ToplevelResponse, InlineCommand
from ..properties import BACKEND_COMMAND, L1TEST_EXCEPTION, VERDICTS
from ..l1test_configuration.l1test_options import EVALUATE_FUNCTIONS_WITH_SAME_NAME
from thonny.plugins.cpython_backend.cp_back import (
    Executor,
    MainCPythonBackend
)
import thonny.plugins.cpython_backend.cp_back
import pickle

BACKEND: MainCPythonBackend = thonny.plugins.cpython_backend.cp_back.get_backend()

class L1TestExecutor(Executor):
    def execute_source(self, source:str, filename:str, mode:str, ast_postprocessors):  
        """Cette fonction est invoquée par la méthode `BACKEND._execute_file(cmd, L1TestExecutor)`
        située en haut de ce fichier.

        Returns:
            dict: doit retourner, obligatoirement, un dictionnaire dont les données sont séralisées.
        """
        assert mode == "exec"
        try:
            evaluator = Evaluator(filename, source)
            selected_line: int = os.environ.get(SELECTED_LINE_VAR)
            if selected_line: # si un seul test a été ciblé
                selected_line = int(selected_line)
                evaluator.set_finder_strategy(FindSelectedL1DoctestStrategy(selected_line))

            evaluate_functions_with_same_name = os.environ.get(EVALUATE_FUNCTIONS_WITH_SAME_NAME_VAR, 'True') == 'True'
            verdicts = evaluator.evaluate(evaluate_functions_with_same_name=evaluate_functions_with_same_name)

            # on récupère la valeur de l'option qui indique si on doit importer le module dans le shell
            import_module_option = True if os.environ.get(IMPORT_MODULE_VAR) == "True" else False     
            # importation du module dans le shell.
            if import_module_option: 
                # importation du module dans le shell.
                self._import_module_in_shell(evaluator.get_module())                                                

            # Sérialiser les données en binaires. 
            serialized_data = pickle.dumps(verdicts)
            # The serialized data should necessary be a dictionary and the returned statement should
            # also be a dictionary
            return {VERDICTS: serialized_data}
        except BaseException as e:
            # pas besoin de sérialiser la valeur du dictionaire car il conteint que des types primitifs.
            return {L1TEST_EXCEPTION: self._build_backend_exception(e, str(e))}

    def _import_module_in_shell(self, module:ModuleType):
        """
        Imports the given `module` into Thonny's shell.
        
        Args:
            module (ModuleType): the module to be imported into the shell.
        """
        import __main__ 
        __main__.__dict__.update(module.__dict__) 
             
    def _build_backend_exception(self, exception:BaseException, message:str):
        """
            Returns a representation of the exception raised by the l1test backend.
            The representation includes the type of the exception and it's message.
            
            Note : the representation should necessary be a dictionary.
        Args:
            exception (BaseException): The raised exception.
            message (str): The message of the exception to be shown in the view.

        Returns:
            dict: a dictionary that contains information about the raised exception.
        """
        return {
                "type_name": exception.__class__.__name__,
                "message": message, 
                "prefix": exception.get_prefix_message() if isinstance(exception, BackendException) \
                                                         else None
            }
 
def _cmd_l1test(cmd: ToplevelCommand) -> ToplevelResponse:   
    """
    Cette fonction est invoquée lorsque un événement de type `ToplevelCommand` (associé 
    à la commande L1test) est récupéré.
    
    Args: 
        cmd(ToplevelCommand): L'événement `ToplevelCommand` associé à la commande L1test.
        
    Returns:
        ToplevelResponse: un événement de type ToplveleResponse qui contiendra la réponse
        renvoyé par `L1TestExecutor.execute_source()`.
    """ 
    response: ToplevelResponse = BACKEND._execute_file(cmd, L1TestExecutor)
    return response

def load_plugin(): 
    """
        Cette fonction est importante car il est appelée par Thonny à son intialisation.
        
        Cette fonction doit déclarer les commandes magiques et leurs handlers.
    """
    BACKEND.add_command(BACKEND_COMMAND, _cmd_l1test)
