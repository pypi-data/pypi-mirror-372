from thonnycontrib.i18n.languages import tr
from thonny import get_workbench
import thonnycontrib.i18n.languages as languages

if get_workbench(): # si l'éditeur est prêt alors on change la langue du translateur.
    languages.set_language(get_workbench().get_option("general.language"))

PLUGIN_NAME = "L1Test"
ERROR_VIEW_LABEL = '%s errors' % PLUGIN_NAME

# ici vous pouvez changer la syntaxe du doctest. 
# version 2022 PJI : Actuellement on garde la syntaxe `$py`.
L1TEST_SYMBOL = "[$]py"
# version 2022 avant la rentrée
L1TEST_SYMBOL1 = "[$][$][$]"
L1TEST_SYMBOL2 = "[$]PY"
L1TEST_SYMBOL3 = "[$]py"
# L'invite des tests qui vérifient la levée d'exception
L1TEST_EXCEPTION_SYMBOL = "[$][$]e"


# ############################################################################################### #
#                       LES NOUVELLES VARIABLES VERSION 2023 PFE                                  #
# ############################################################################################### #

# Le nom de la commande magique pour l1test(doit toujours commencer par une majuscule)
BACKEND_COMMAND = "L1test"


# ############ Les noms des clés du dictionnaire renvoyé par le l1test_backend ############
# Le nom de l'attribut contenant les résulats des tests renvoyés par l1test_backend
VERDICTS = "verdicts"
# Le nom de l'attribut contenant une exception levée et renvoyée par l1test_backend
L1TEST_EXCEPTION = "l1test_exception"

# ############ Les labels des buttons du menu l1test treeview ############
PLACE_RED_TEST_ON_TOP_LABEL = tr("Place the red tests on the top")
RESUME_ORIGINAL_ORDER = tr("Resume original order")
SHOW_ONLY_RED_TESTS = tr("Show only red tests")
SHOW_ALL_TESTS = tr("Show all the tests")
EXPAND_ALL = tr("Expand all functions")
FOLD_ALL = tr("Fold all functions")
UPDATE_FONT_LABEL = tr("Update the font")
INCREASE_SPACE_BETWEEN_ROWS = tr("Increase row height")
DECREASE_SPACE_BETWEEN_ROWS = tr("Decrease row height")
CLEAR = tr("Clear")

# Le message affiché sur la treeview quand `l1test` est en cours d'execution
L1TEST_IN_PROGRESS = tr("Executing tests in progress")

# Le message affiché sur la treeview quand il n'existe aucun test
NO_TEST_FOUND_MSG = tr("No test found !")

# The title of the error view when the docstring genertor shows the raised error
CANNOT_GENERATE_THE_DOCSTRING = tr("Cannot generate the docstring :")
# The title of the error view when the l1test shows the raised error
CANNOT_RUN_TESTS_MSG = tr("Cannot run %s :")%(PLUGIN_NAME)

# These are the states sent by the evaluator to the L1TestRunner to indicate whether or not test execution has been completed.
PENDING_STATE = "Pending"  # this state indicates that an Example (a test) is still evaluating. This state is sent for each Example (as test).
FINISHED_STATE = "Finished" # this state indicates that the Evaluator has finished it's job and all the evalutions are done. This state is sent after all the evaluation.

# A special event that `L1TestTreeview` sends to `L1TestRunner` when clicking on an exception test
# The event transfers the details of the clicked exception to the `L1TestRunner` 
# which will show it in the error view.
L1TREE_VIEW_EVENT = "L1TreeviewEvent"

# Les images utilisées par la treeview
PENDING_ICON = "pending_icon.png"
ERROR_ICON = "error_icon.png"
RESTART_ICON = "restart_icon.png"
FAILED_RED_CHIP = "failed_red_chip.png" # le petit cercle rouge qui précède un test qui a échoué
EXCEPTION_RED_CHIP = "exception_red_chip.png" # le petit cercle rouge (avec un poitn d'exclamation) qui précède un test qui a échoué
SUCCESS_GREEN_CHIP = "success_green_chip.png" # le petit cercle vert qui précède un test qui a réussi
