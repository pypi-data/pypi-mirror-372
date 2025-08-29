from collections import namedtuple
from typing import List

from ..utils import clear_env_vars
from ..backend.ast_parser import L1DocTest
from ..exceptions import *
from ..environement_vars import *
from .l1test_reporter import *
from ..properties import *
from ..l1test_configuration.l1test_options import EVALUATE_FUNCTIONS_WITH_SAME_NAME
from thonny.common import ToplevelResponse, InlineResponse
from thonny.workbench import WorkbenchEvent
from thonnycontrib import frontend 
from thonny.editors import EditorNotebook
from thonny import editors
import thonny
from ..ThonnyLogsGenerator import log_in_thonny
import pickle, inspect, thonny
from ..l1test_configuration import l1test_options 
from ..i18n.languages import tr


# ErrorMsg déclare deux champs : le préfixe et le message d'erreur
# le préfix est juste le titre qui précède le message d'erreur sur la Error view
ErrorMsg = namedtuple("ErrorMsg", "title msg")

# Le nom de l'event qui lance le redémarrage du backend thonny
BACKEND_RESTART_EVENT = "BackendRestart"

class L1TestRunner:
    """
        The `L1TestRunner` is responsible for starting the execution of the plugin. It's like 
        a controller that handles sending requests and receiving responses.

        Firstly, it sends a request to the backend to evaluate the current source code. Then,
        it handles the response receieved from the backend and parses it. The backend
        send a response of type `TopLevelResponse` that contains results computed by the `Evaluator`.
        The results can be the verdicts if it succeed or an exception if failed. 
        In the both of case, `L1TestRunner` decides and invokes the `L1TestReporter` to show 
        either the verdicts or the error message.
        
        The L1TestRunner handles also the state of the current execution of the plugin. It has 
        three states : 
        - _is_l1test_running : set to true when the button l1test is just invoked.
        - _is_pending : set to true when the plugin is still runinng but not yet finished. 
                        This state is sent from the backend to tell the `L1TestRunner` that the `Evaluator`
                        didn't finished the evaluations yet. This is useful when the Evaluator encouter
                        an infinite loop, in this case the L1TestRunner knows that the Evaluator is still 
                        working (or blocked) but at the same time the L1testRunner shows the current state
                        in the view. This is handy for junior devs to tell them why the plugin is still
                        turning.
        - _has_exception: when the backend sends an error message instead of the verdicts.

        Note: `L1TestRunner` does not deal with the construction of the views but 
        it allows to invoke the correct one. 
    """
    def __init__(self, reporter=None):
        frontend._l1test_runner = self
        
        self._reporter = L1TestReporter() if not reporter else reporter
        self._has_exception = False
        self._is_l1test_running = False
        self._is_pending = False
        self._has_reported_exception = False # indique si une ligne d'erreur de la tree a été clique et que l'exception
                                            # a été reporté sur la ErrorView
        self._filename = "<module>"
        # Quand le backend envoie une réponse de type `ToplevelResponse``,
        # alors le TestRunner va invoquer la fonction `show_verdicts`
        thonny.get_workbench().bind("ToplevelResponse", self._handle_backend_response, True)
        
        # Quand le backend envoie une réponse de type `InlineResponse``,
        # alors le TestRunner va invoquer la fonction `show_execution_state`
        thonny.get_workbench().bind("InlineResponse", self._handle_execution_state, True)
        
        thonny.get_workbench().bind(L1TREE_VIEW_EVENT, self._handle_clicked_exception, True)
        
        # Quand le backend est redémarré en thonny nous invoquons la méthode 
        # `self._on_restart_backend()`
        thonny.get_workbench().bind(BACKEND_RESTART_EVENT, self._on_restart_backend, True)
    
    def run_l1test(self, selected_line: int=None):
        """
        Run the L1Test plugin by sending a command to the l1test_backend. This method checks
        if the file is saved and if the editor is empty. If the file is not saved or the editor
        then it will display an error message on the ErrorView. Otherwise, it will send a command 
        to the backend to run the tests.
        Args:
            is_selected (bool): Set as True if only one method is selected to run
                            it's tests.
            selected_line (int): The number of the selected line. 
            Default is 0 if no line is selected.
        """
        try:
            editor: EditorNotebook = get_workbench().get_editor_notebook()
            # si aucun editeur n'est ouvert sur le workbench
            if not editor.get_current_editor():
                raise NoEditorFoundException(tr("No editor found !\n\nPlease open an editor before running the tests."))
            
            # cette ligne demande de sauver le fichier s'il n'a pas encore été sauvé sur
            # la machine. Si le fichier est déjà sauvé, il va permettre d'enregistrer la nouvelle
            # version du fichier.
            filename = editors.get_saved_current_script_filename(force=True)          

            # si le filename est null alors le fichier n'a  pas été sauvé sur machine.  
            # Ce cas survient quand l'utilisatur quitte la fenetre de sauvegarde sans sauver le fichier.
            if not filename: 
                msg = tr("The file is not saved.\n\nConsider to save the file before running the tests.")
                raise NotSavedFileException(msg)

            self._filename = filename
            
            if not editor.get_current_editor_content().strip():  # L'éditeur est vide. 
                # on a pas envie d'envoyer une commande au backend si le fichier est vide.
                # Dans tous les cas y a rien à tester.
                raise EmptyEditorException(tr("The editor is empty!\n"))
            
            # si on est là alors le fichier est bien sauvegardé et contient quelque chose.
            self.request_backend(selected_line)         
        except FrontendException as e: # on catche que les exception coté view
            self.terminate_running()
            self.set_has_exception(True) 
            self.show_error_view(str(e))
    
    def request_backend(self, selected_line:int, already_retried: bool = False):
        """Allows to execute the `L1test` magic command. 
        
        There's two cases : 
        1. if the `L1test` is invoked only one time so the command is sent to 
        backend to be executed by the thonny's runner. 
        2. if the `L1test` is invoked a lot of times (lot of clicks), then we only
        consider the first invocation (first click) of the `L1test` command. While 
        the l1test still running, the other clicks are ignored.

        Args:
            selected_line (int): The number of the selected line.
        """
        treeview = self._reporter.get_treeview()
        if not self.is_running(): # si l1test n'est est pas déjà en cours d'execution
            try:
                # si le backend n'est pas en cours prêt à recevoir une commande.
                # cette vérification est nécessaire pour éviter le problème décrit 
                # dans l'issue #17 (https://gitlab.univ-lille.fr/reda.idtaleb.etu/thonny_test_framework/-/issues/17)
                if not thonny.get_runner().is_waiting_toplevel_command(): 
                    raise BackendNotReadyYetException(tr("The backend is not ready yet !"))
                # si on est là alors le backend est prêt à recevoir une commande
                self.set_is_running()
                # appelle la commande magique L1test
                self.__request_backend(selected_line=selected_line)
            except BackendNotReadyYetException as e:
                # si le backend n'est pas prêt à recevoir une commande alors on
                # attend 1 seconde avant de réessayer. 
                self.set_is_running(False)
                treeview.insert_in_header(tr("Waiting for the backend to restart completely ..."), 
                                          clear=True, tags=("red"), image=ERROR_ICON)
                if not already_retried: # on essaie une seconde fois, sinon on arrête
                    thonny.get_workbench().after(1000, self.request_backend, selected_line, True)
            except:
                self.set_is_running(False)
                treeview.insert_in_header(tr("Coudn't restart the backend.\nPlease restart with the 'Stop' button !"), 
                                          clear=True, tags=("red"), image=ERROR_ICON)
            finally:
                clear_env_vars(IMPORT_MODULE_VAR, SELECTED_LINE_VAR)

    def __request_backend(self, command_name=BACKEND_COMMAND, selected_line:int=None):
        """
        Sends a command to the Thonny's backend to execute the current script.
        The name of the command must starts with a uppercase.    
        
        Please note that `thonny.get_runner.execute_current()` will consider 
        all the current script, and it builds a `ToplevelCommand` automatically. 
        So in the case if you don't want to consider all the script but only a 
        selected method, you should set the number of the selected line. 
        
        The value of the selected line is stored in an environnement variable to be
        shared with the backend. The handler of the command(l1test_backend) can access 
        this environnement variables to decide if the `Evaluator` should run all the 
        tests or only for the selected line.

        Note: the value of the environnement variable should be a string.
        For example : 
        ```py
        os.environ["is_selected"] = str(is_selected) # the value should always be a string 
        ```
        
        In the handler of the command :
        ```py
        def _cmd_l1test(cmd: ToplevelCommand):         
            is_selected: bool = eval(os.environ.get("is_selected"))
        ```
                    
        Note : when a new command is called in Thonny it triggers a partial 
        "restart" of the backend before processing the new command. Thonny does 
        this to force stop the current process and start a new process for the 
        new command.
            
        Args:
            command_name (str): A command name , should starts with a upper case. 
            Defaults to BACKEND_COMMAND.
            selected_line (int, optional): The number of the selected line. Defaults to None
            if no line is selected.
        """ 
        # on stocke dans une variable d'environnment la valeur de l'option `import_module in shell`.
        # le l1test backend retrouvera cette valeur pour décider d'importer ou non le module dans le shell.
        os.environ[IMPORT_MODULE_VAR] = str(l1test_options.get_option(l1test_options.IMPORT_MODULE))
        os.environ[EVALUATE_FUNCTIONS_WITH_SAME_NAME_VAR] = str(l1test_options.get_option(l1test_options.EVALUATE_FUNCTIONS_WITH_SAME_NAME))
        
        if selected_line:
            os.environ[SELECTED_LINE_VAR] = str(selected_line)
        
        # Une fois que execute_current() est executée un restart backend partiel est invoqué
        # pour un nouveau processus pour la commande passé en paramètre.
        thonny.get_runner().execute_current(command_name)

    def _handle_backend_response(self, msg: ToplevelResponse):     
        """
        This method is binded to the `TopLevelResponse` event sent by the backend.
        
        If this method is triggered so the `msg` parameter will contain the response received 
        from the backend. Please note that the `TopLevelResponse` event is not necessary sent 
        by the l1test_backend, but it can be also sent by the Shell. The shell contains an 
        internal infinite loop that waits for commands and sends the responses periodically.
        
        This method verify the source of the `TopLevelResponse` event. If the source is 
        l1test_backend so it checks the recieved response if it contains exception or not. 
        If the response contains an exception so the according error will be displayed in 
        error view. Otherwise the response contains the verdicts of the tests and will be shown 
        on the treeview.
        
        Note: The data is deserialized before displaying it on the view.
        """   
       
        # On vérifie si le TopLevelRespone reçu est envoyé par le l1test_backend 
        if self._is_relevant_response(msg):
            verdicts, error_msg = self.__get_verdicts_and_error(msg)
            if not self.has_exception(): 
                self.set_and_show_verdicts_on_treeview(verdicts) 
            else: 
                self.clean_treeview()
                self.show_error_view(error_msg.msg, error_msg.title)
        else:
            # Le TopLevelReponse reçu ne nous intéresse pas.
            return 
        # On indique l'état de l'execution du la commande comme terminée
        self.terminate_running()
    
    def __get_verdicts_and_error(self, msg:ToplevelResponse) -> tuple[List[L1DocTest], ErrorMsg]:
        """
        Returns the l1doctests and the error message from the received response. 
        If the response contains an exception so the error message will be returned. In this
        case the l1doctests will be None. Reverse is true, if the response does not contain the
        error message so the l1doctests will be returned and the error message will be None.
        
        Args:
            msg (ToplevelResponse): The received response from the backend.

        Returns:
            a tuple of (l1doctests, error_msg)
        """
        l1doctests, error_msg = None, ErrorMsg(title=None, msg=None)
        self.clean_error_view()
        if not self.is_pending() and (self.is_running() or msg.get("command_name") == BACKEND_COMMAND): # si le plugin est en cours d'execution et n'est pas en attente (càd pas de tests en cours d'execution) OU si on utilise la commande magique %L1test
            self.clean_treeview()
            received_verdicts = msg.get(VERDICTS)
            if received_verdicts: # si les verdicts sont présents on les désérialize en liste de L1DocTest
                self.set_has_exception(False)
                # deserialize the verdicts
                l1doctests: List[L1DocTest] = pickle.loads(received_verdicts)
                # log in thonny                    
                log_in_thonny(l1doctests, self._filename, os.environ.get(SELECTED_LINE_VAR) != None)
            else: # si les verdicts sont None alors c'est une exception qui a été levée par le backend
                error_msg = self.__handle_raised_exception(msg.get(L1TEST_EXCEPTION))
        return l1doctests, error_msg
    
    def __handle_raised_exception(self, exception: dict) -> ErrorMsg:
        """
        This function handles the raised exception by returning a tuple containing
        a prefix message and the exception message.

        The prefix refers to the title shown on the ErrorView. If you want to remove 
        the title, you should specify the prefix as an empty string. If you don't 
        want to change the title, you should specify the prefix as `None`.
        
        Note: this function also sets the state of the execution. It set the `_has_exception`
        attribute to True if the exception is not an `InterruptedError`. Otherwise, it
        sets the `_has_exception` attribute to False.
        
        Args:
            exception (dict): The exception to handle.

        Returns:
            ErrorMsg: a couple that indicates a prefix message and the exception message.
        """
        if exception.get("type_name") == InterruptedError.__name__:
            self.set_has_exception(False)  # ce n'est pas une erreur
            self.clean_treeview()
            
            return ErrorMsg(title=None, msg=None)    # On fait rien.
        
        self.set_has_exception(True)   # on indique l'état de l'execution
        
        # The backend exceptions inherit from the BackendException class
        backend_exceptions = self.__get_all_backend_exceptions()
        
        for backend_exception in backend_exceptions:                
            if (exception.get("type_name") == backend_exception.__name__) :
                return ErrorMsg(exception.get("prefix"), exception.get("message")) 
        
        # si on est là alors l'exception levée n'est pas une exception backend est
        # c'est probablement une exception levée par python.
        return ErrorMsg(title=exception.get("prefix"), 
                        msg="%s:\n%s" % (exception.get("type_name"), exception.get("message")))
    
    def __get_all_backend_exceptions(self) -> list[BackendException]:
        """
        All the exceptions (specifc to l1test) raised on the backend 
        inherit from the `BackendException` class.
        
        Gets dynamically the exceptions inherit from the `BackendException` class that
        are declared in the `exceptions.py` module.

        Returns:
            list[BackendException]: Returns a list of the backend exception classes.
        """
        import thonnycontrib.exceptions as exceptions
        backend_exceptions = []
        for name, obj in inspect.getmembers(exceptions):
            if inspect.isclass(obj) and issubclass(obj, exceptions.BackendException):
                backend_exceptions.append(obj)
        return backend_exceptions   
    
    def _on_restart_backend(self, event: WorkbenchEvent):
        """
        This function is called when the backend of thonny is restared. The restarting
        of the backend generates a `BackendRestart` event and this event can 
        be generated either by  the red `Stop/Restart backend` button in Thonny's 
        toolbar or by invoking a new command. 
        
        When a new command is called in Thonny it triggers a partial restart
        of the backend before processing the command. Thonny does this to stop
        the current process and start a new process for the new command.

        This function tries to verify if the backend is restarted by clicking the red button
        or by invoking the `l1test_command`. 
            - if the backend is restarted by clicking the red button, so the treeview is cleaned.
            - if the backend is restarted by invoking the `l1test_command`, so we show in the
            treeview that the l1test is being executed.
            - if the backend is restarted by invoking an other command, so nothing is done.
        
        The problem is that we cannot know who generates the `BackendRestart` event. So to know 
        if the `BackendRestart` event is generated by the `l1test_command` we use the attribute 
        `self._is_l1test_running`. This attribute was setted to True before sending the 
        `l1test_command` to the backend.
        
        Args:
            event (WorkbenchEvent): The event generated from backend restart.
        """
        if (event.get("sequence") == BACKEND_RESTART_EVENT):   
            # Quand le backend est redémarré on efface les exceptions récemment affichée par l1test 
            self.set_has_exception(False)
            self.clean_error_view() 
            
            treeview:L1TestTreeView = self._reporter.get_treeview()
            treeview.disable_menu()
            # L'attribut "full" est un boolean, si c'est "True" alors le backend procède a un
            # redémarrage complet (c'est le cas quand on appuit sur le bouton rouge Stop/Restart).
            # Si c'est False alors c'est un redémarrage partiel du backend (c'est le cas d'un appel 
            # d'une nouvelle commande).
            if event.get("full"):
                self.terminate_running()
                self.clean_treeview(clear_all=True, clear_verdicts_data=True) 
            elif self.is_running(): # si le plugin a été lancé par l'utilisateur
                self.clean_treeview(clear_all=True, clear_verdicts_data=True) 
                treeview.insert_in_header(tr("Starting executing tests ..."), clear=True, tags="gray", 
                                            image=PENDING_ICON)
            else: # probablement une autre commande a déclenché le Restart du backend -> on fait rien
                pass
            self.hide_errorview_and_show_treeview()
    
    def _handle_execution_state(self, msg: InlineResponse):
        """
        This function is called when an event of type InlineResponse is received. 
        This function verifies the source of the event. If the source is L1Test so it will access to the 
        received response and then it will handle the state of the execution.
        """
        if self._is_relevant_response(msg):
            state:str = msg.get("state")
            if state == PENDING_STATE:
                lineno = msg.get("lineno") # la ligne en cours d'execution est récupéré seulement si le state == PENDING_STATE
                status_msg = L1TEST_IN_PROGRESS + ": line " + str(lineno) 
                # you can uncomment the following line if you want to show the current executed line
                #self._reporter.get_treeview().insert_in_header(status_msg, clear=True, tags="gray", image=PENDING_ICON)
                self.set_pending(True)
            else: # si le state == FINISHED_STATE
                self.set_pending(False) 
    
    def show_error_view(self, error_msg=None, error_title=None, force=False, show_treeview=False):
        if self._has_exception or force:
            self.show_errors(exception_msg=error_msg, title=error_title)
            self._reporter.get_error_view().show_view()   
            if show_treeview:
                self._reporter.get_treeview().show_view()
            else: 
                self._reporter.get_treeview().hide_view()
    
    def set_and_show_verdicts_on_treeview(self, verdicts:List[L1DocTest]):
        if not self._has_exception:
            self.set_and_show_verdicts(verdicts)     
            self.hide_errorview_and_show_treeview()
    
    def hide_errorview_and_show_treeview(self):
        if self.is_running():
            self._reporter.get_treeview().show_view()
            self.clean_error_view()
            self._reporter.get_error_view().hide_view()
            
    def _handle_clicked_exception(self, event:WorkbenchEvent=None):
        """ 
        This function is called when the user clicks on an exception in the treeview. Then, 
        the error view is displayed with the details of the clicked exception. 
        """
        possible_keys = ["sequence", "error_title", "error_msg", "side_by_side"]
        if event and event.get("sequence") == L1TREE_VIEW_EVENT:
            assert all(key in possible_keys for key in event.__dict__.keys())
            self.set_has_reported_exception(True)
            self.show_error_view(error_msg=event.error_msg, 
                                  error_title=event.error_title, 
                                  force=True,
                                  show_treeview=event.side_by_side)
            
    def set_and_show_verdicts(self, test_results:List[L1DocTest]):
        """
        Report the verdicts on the view.

        Args:
            test_results (dict): The recieved verdicts from the backend.
        """
        self._reporter.display_tests_results(test_results) 
    
    def show_errors(self, exception_msg, title=None):
        """
        Clears the error view and reports the error message on it.
        
        Args:
            exception_msg (str): The error message to display.
            title (str, optional): The title of the error message. Defaults to None.
        """
        title = CANNOT_RUN_TESTS_MSG if title is None else title
        self._reporter.display_error_msg(exception_msg, title=title) 
    
    def _is_relevant_response(self, msg: ToplevelResponse, cmd_name:str=BACKEND_COMMAND):
       """Returns True if the TopLevelResponse is relevant to the l1test plugin."""         
       return msg.get("command_name") == cmd_name
    
    def clean_error_view(self):
        self._reporter.get_error_view().clear()
               
    def clean_treeview(self, clear_verdicts_data=False, clear_all=True, clear_errorview=False): 
        self._reporter.get_treeview().clear_tree(clear_verdicts_data=clear_verdicts_data, 
                                                 clear_all=clear_all, 
                                                 clear_errorview=clear_errorview)
         
    def set_is_running(self, value=True):
        self._is_l1test_running = value
    
    def is_running(self):
        return self._is_l1test_running
    
    def is_pending(self):
        return self._is_pending
    
    def set_pending(self, is_pending:bool):
        self._is_pending = is_pending
    
    def set_has_exception(self, has_exception:bool):
        self._has_exception = has_exception
    
    def has_exception(self):
        return self._has_exception
    
    def terminate_running(self):
        """
        Set the state of `L1TestRunner` as terminated.
        This function sets the `_is_l1test_running` attribute to False
        """
        self.set_pending(False)
        self.set_is_running(False)
        
    def get_reporter(self) -> L1TestReporter:
        return self._reporter
    
    def set_reporter(self, reporter):
        self._reporter = reporter

    def has_reported_exception(self):
        return self._has_reported_exception
    
    def set_has_reported_exception(self, value:bool):
        self._has_reported_exception = value
