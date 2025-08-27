from ..imports import *
from abstract_gui.QT6 import attach_textedit_to_logs
def _on_filter_mode_changed(self):
    self.fn_filter_mode = "source" if self.rb_fn_source.isChecked() else ("all" if self.rb_fn_all.isChecked() else "io")
    if self.current_fn:
        self._render_fn_lists_for(self.current_fn)
def _on_filter_mode_changed(self):
    self.fn_filter_mode = "source" if self.rb_fn_source.isChecked() else ("all" if self.rb_fn_all.isChecked() else "io")
    if self.current_fn:
        self._render_fn_lists_for(self.current_fn)

def _render_fn_lists_for(self, fn_name: str=None):
   fn_name = fn_name or self.current_fn
   self._render_symbol_lists_for(fn_name, self.func_map,
                             self.exporters_list, self.importers_list,
                             getattr(self, "fn_filter_mode", "io"))
   
# functionsTab/functionsTab/functions/filter_utils.py
def _on_map_ready(self, graph: dict, func_map: dict, var_map: dict | None = None):
    self.graph   = graph or {}
    self.func_map = func_map or {}
    self.var_map  = var_map  or {}   # <-- new

    # functions
    self._rebuild_fn_buttons(sorted(self.func_map.keys()))
    if self.current_fn and self.current_fn in self.func_map:
        self._render_fn_lists_for(self.current_fn)
    elif self.func_map:
        self._on_function_clicked(sorted(self.func_map.keys())[0])

    # variables
    if hasattr(self, "_rebuild_var_buttons"):
        self._rebuild_var_buttons(sorted(self.var_map.keys()))

    self.appendLog(f"[map] UI updated: {len(self.func_map)} functions, {len(self.var_map)} variables\n")
