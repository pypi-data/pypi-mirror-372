from thonny.workbench import Workbench
from typing import Any, Callable
import tkinter as tk

class MockWorkbench(Workbench):
    def __init__(self):
        self._view_records = {}
        pass
    
    def add_view(self, cls, label: str, default_location: str, visible_by_default: bool = False, default_position_key = None,
    ) -> None:
        view_id = cls.__name__
        self._view_records[view_id] = {
                "class": cls,
                "label": label,
                "location": "nw",
                "position_key": "A",
                "visibility_flag": None,
            }
        
    def get_view(self, view_id: str, create: bool = True) -> tk.Widget:
        if "instance" not in self._view_records[view_id]:
            if not create:
                raise RuntimeError("View %s not created" % view_id)
            class_ = self._view_records[view_id]["class"]
            # create the view
            view = class_()  # View's master is workbench to allow making it maximized
            self._view_records[view_id]["instance"] = view
            view.hidden = True
        return self._view_records[view_id]["instance"]
    
    def get_option(self, name: str, default=None) -> Any:
        if name in ("view.editor_font_family", "view.io_font_family"):
            return ""
        elif  name == "view.editor_font_size":
            return 0
        # Need to return Any, otherwise each typed call site needs to cast
        return self._configuration_manager.get_option(name, default)
    
    def bind(self, sequence: str, func: Callable, add: bool = None) -> None:
        pass
    
    def show_view(self, view_id: str, set_focus: bool = True) :
        return 
    
    def hide_view(self, view_id: str) :
        return None
