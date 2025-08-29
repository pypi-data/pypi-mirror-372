from thonnycontrib.frontend.l1test_runner import L1TestRunner
from thonnycontrib.frontend.l1test_reporter import L1TestTreeView, L1TestErrorView
from thonnycontrib.backend.doctest_parser import *
from unittest.mock import *
from thonny.workbench import WorkbenchEvent
import unittest as ut, thonny
from thonnycontrib.properties import PLUGIN_NAME
from thonnycontrib.tests.fixtures.workbench_mock import *


# ##############################################################
#    Tous les tests qui suivent testent la classe L1TestRunner
# ##############################################################


class TestTestRunner(ut.TestCase):
    def setUp(self) -> None:
        self.workbench_event = WorkbenchEvent(sequence="BackendRestart")
    
    def tearDown(self) -> None:
        del self.workbench_event 
    
    """
    Quand un restart backend complet(ex.via le button rouge) est réalisé,
    alors on doit s'assurer que:
    - L'état de `l1TestRunner` est déclaré comme terminé.
    - Le contenu de la treeview est vide.
    """
    @patch("thonny.get_workbench", return_value=MockWorkbench())
    def test_restart_backend_event_when_complete_restart(self, mock_get_workbench: MagicMock):
        self.__add_views()
        l1test_runner = L1TestRunner()
        
        # on s'assure que le mock_get_workbench est appelée lors de l'instantiation de L1TestRunner
        mock_get_workbench.assert_called()
        
        # On doit ajouter du faux contenus à la treeview, pour vérifier qu'elle
        # sera vraiment nettoyée après le restart_backend.
        l1test_treeview = l1test_runner.get_reporter().get_treeview()
        treeview = self.__add_fake_row_in_treeview(l1test_treeview)
        
        self.workbench_event.full = True # on suppose que c'est un redémarrage complet
        l1test_runner._on_restart_backend(self.workbench_event)

        # on s'assure qu'après le redémarrage complet du backend l'état du `L1TestRunner` est déclaré 
        # comme terminé.
        self.assertFalse(l1test_runner.is_running())
        
        # on s'assure que le contenu de la treeview est vide
        self.assertTrue(len(treeview.get_children()) == 0)
    
    """
    Si un restart backend partiel(ex. invocation d'une nouvelle commande magique) est appelé
    après l'invocation de la commande magique `L1test`, alors on doit s'assurer que:
    - Le `l1TestRunner` est en execution.
    - La treeview et effacée.
    
    Le cas de ce test : la treeview était initialement vide.
    """
    @patch("thonny.get_workbench", return_value=MockWorkbench())
    def test_restart_backend_event_when_partial_restart_and_when_l1test_is_invoked_case1(self,  
        mock_get_workbench: MagicMock
    ):
        
        self.__add_views()
        l1test_runner = L1TestRunner()
        
        # on s'assure que le mock_get_workbench est appelée lors de l'instantiation de L1TestRunner
        mock_get_workbench.assert_called()
        
        # on suppose que la commande L1test a été invoquée
        l1test_runner.set_is_running()
        # On s'assure que le `L1TestRunner` est en execution.
        self.assertTrue(l1test_runner.is_running())
        
        self.workbench_event.full = False # on suppose que c'est un redémarrage partiel
        l1test_runner._on_restart_backend(self.workbench_event)

        treeview = l1test_runner.get_reporter().get_treeview().get_treeview()
        # on s'assure qu'il existe rien dans la treeview
        self.assertTrue(len(treeview.get_children()) == 0)

    """
    Si un restart backend partiel(ex. invocation d'une nouvelle commande magique) est appelé
    après l'invocation de la commande magique `L1test` alors on doit s'assurer que:
    - Le `l1TestRunner` est en execution.
    - La treeview est vide.
    
    Le cas de ce test : la treeview était initialement remplie.
    """
    @patch("thonny.get_workbench", return_value=MockWorkbench())
    def test_restart_backend_event_when_partial_restart_and_when_l1test_is_invoked_case2(self,  
        mock_get_workbench: MagicMock
    ):
        self.__add_views()
        l1test_runner = L1TestRunner()
        
        # on s'assure que le mock_get_workbench est appelée lors de l'instantiation de L1TestRunner
        mock_get_workbench.assert_called()
        
        # on suppose que la commande L1test a été invoquée
        l1test_runner.set_is_running()
        # On s'assure que le `L1TestRunner` est en execution.
        self.assertTrue(l1test_runner.is_running())
        
        # On doit ajouter du faux contenus à la treeview, pour vérifier que son contenue
        # sera effacée et que le message "Executing tests in progress ..." apparaîtera à la place
        l1test_treeview = l1test_runner.get_reporter().get_treeview()
        treeview = self.__add_fake_row_in_treeview(l1test_treeview)
        
        self.workbench_event.full = False # on suppose que c'est un redémarrage partiel
        l1test_runner._on_restart_backend(self.workbench_event)
        
        # On s'assure qu'il y a rien dans la treeview
        self.assertTrue(len(treeview.get_children()) == 0)
    
    """
    Si un restart backend partiel(ex. invocation d'une nouvelle commande magique) est appelé
    après une autre commande magique(pas `L1test`), alors on doit s'assurer que:
    - Le `l1TestRunner` n'est pas en execution.
    - Le contenu de la treeview n'est pas effacée.
    """
    @patch("thonny.get_workbench", return_value=MockWorkbench())
    def test_restart_backend_event_when_partial_restart_and_when_l1test_is_not_invoked(self,  
            mock_get_workbench: MagicMock
    ):
        self.__add_views()
        l1test_runner = L1TestRunner()
        
        # on s'assure que le mock_get_workbench est appelée lors de l'instantiation de L1TestRunner
        mock_get_workbench.assert_called()
        
        # On s'assure que le `L1TestRunner` n'est pas en execution.
        self.assertFalse(l1test_runner.is_running())
        
        # On doit ajouter du faux contenus à la treeview, pour vérifier que le contenu
        # de la treeview ne sera pas du tout effacée.
        l1test_treeview = l1test_runner.get_reporter().get_treeview()
        row_text = "A fake content"
        treeview = self.__add_fake_row_in_treeview(l1test_treeview, row_text=row_text)
        
        self.workbench_event.full = False # on suppose que c'est un redémarrage partiel
        l1test_runner._on_restart_backend(self.workbench_event)
        
        # on s'assure que le contenu de la treeview reste le même 
        self.assertTrue(len(treeview.get_children()) == 1)
        for child_id in treeview.get_children():
            # on doit vérifier le contenu de la ligne ajoutée
            self.assertTrue(row_text in treeview.item(child_id)["text"])
    
    """
    Adds one fake row to the treeview and asserts that the row is well
    added to the treeview.
    
    Returns: 
        Widget(tk.Treeview): if the assertions are passed so the treeview with the added row
        will be returned.
    """
    def __add_fake_row_in_treeview(self, l1test_treeview: L1TestTreeView, row_text="A fake content"):
        # on s'assure que la ligne est bien ajoutée à la treeview
        treeview = l1test_treeview.get_treeview()
        treeview.insert("", "end", text=row_text)
        self.assertTrue(len(treeview.get_children()) == 1)
        for child_id in treeview.get_children():
            # on doit vérifier le contenu de la ligne ajoutée
            self.assertTrue(row_text in treeview.item(child_id)["text"])
        return treeview
        
    def __add_views(self):
        Workbench = thonny.get_workbench()
        Workbench.add_view(L1TestTreeView, PLUGIN_NAME, "nw")
        Workbench.add_view(L1TestErrorView, '%s errors' % PLUGIN_NAME, "sw")
        

if __name__ == '__main__':
    ut.main(verbosity=2)   
