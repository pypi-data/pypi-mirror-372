import unittest
from unittest.mock import Mock, patch
from thonnycontrib.l1test_configuration.l1test_options import get_option, PLUGIN_NAME

DEFAULT_DOCSTRING_PATTERN_DEF = """\"\"\" à_remplacer_par_ce_que_fait_la_fonction

Précondition : 
Exemple(s) :
$$$ 
\"\"\"
"""
DEFAULT_DOCSTRING_PATTERN_CLASS = """\"\"\" à_remplacer_par_ce_que_fait_la_classe

Exemple(s) :
$$$ 
\"\"\"
"""

class TestL1TestOptions(unittest.TestCase):

    @patch('thonnycontrib.l1test_configuration.l1test_options.get_workbench', return_value=Mock())
    def test_get_option_for_function(self, mock_get_workbench):
        # Définir une valeur de retour pour le mock de get_option
        mock_get_workbench.return_value.get_option.return_value = DEFAULT_DOCSTRING_PATTERN_DEF

        # Appeler la fonction get_option
        option_name = "docstring_pattern_def"
        result = get_option(option_name)

        # Vérifier que get_option a été appelé avec le bon nom d'option
        mock_get_workbench.return_value.get_option.assert_called_once_with("%s.%s" % (PLUGIN_NAME, option_name))

        # Vérifier que la valeur retournée par get_option est correcte
        self.assertEqual(result, """\"\"\" à_remplacer_par_ce_que_fait_la_fonction

Précondition : 
Exemple(s) :
$$$ 
\"\"\"
""")
        
    @patch('thonnycontrib.l1test_configuration.l1test_options.get_workbench', return_value=Mock())
    def test_get_option_for_class(self, mock_get_workbench):

        # Définir une valeur de retour pour le mock de get_option
        mock_get_workbench.return_value.get_option.return_value = DEFAULT_DOCSTRING_PATTERN_CLASS

        # Appeler la fonction get_option
        option_name = "docstring_pattern_class"
        result = get_option(option_name)

        # Vérifier que get_option a été appelé avec le bon nom d'option
        mock_get_workbench.return_value.get_option.assert_called_once_with("%s.%s" % (PLUGIN_NAME, option_name))

        # Vérifier que la valeur retournée par get_option est correcte
        self.assertEqual(result, """\"\"\" à_remplacer_par_ce_que_fait_la_classe

Exemple(s) :
$$$ 
\"\"\"
""")

if __name__ == '__main__':
    unittest.main()