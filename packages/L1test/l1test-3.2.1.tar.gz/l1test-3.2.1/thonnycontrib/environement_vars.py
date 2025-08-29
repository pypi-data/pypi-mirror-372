r""" 
Içi, vous retrouverez les variables d'environnements utilisées par le l1test_backend
-----------------------------------------------------------------------------------

Il n'existe pas de moyens pour acheminer les données necessaires au traitement 
de la commande par l1test_backend. Pour cela, les plugins backend existant passent 
par enregistrer les données comme variable d'environement, ainsi le l1test_backend 
peut retrouver la donnée et décider comment executer ses tests. 

Note: Les variables d'environnements ne persistent pas après la fermeture de Thonny.
"""

# `IMPORT_MODULE_VAR` est une variable d'environnment qui stocke la valeur de l'option
# `l1test_options.IMPORT_MODULE` qui indique si oui(`True`) ou non(`False`) qu'il faut
# importer le module executé dans le shell.
IMPORT_MODULE_VAR = "import_module"

# `SELECTED_LINE_VAR` est une variable d'environnment qui stocke le numéro de ligne de 
# la fonction séléctionnée si `IS_SELECTED_VAR` est à True, sinon elle stocke `None`.
SELECTED_LINE_VAR = "selected_line"

# `EVALUATE_FUNCTIONS_WITH_SAME_NAME_VAR` est une variable d'environnement qui stocke la
# valeur de l'option `l1test_options.EVALUATE_FUNCTIONS_WITH_SAME_NAME`
EVALUATE_FUNCTIONS_WITH_SAME_NAME_VAR = "L1TEST_EVALUATE_FUNCTIONS_WITH_SAME_NAME"
