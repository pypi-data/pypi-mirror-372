from ..imports import *
# --- shared helpers -----------------------------------------------------------
def _normalize_map_entry(data) -> tuple[list[str], list[str]]:
    """
    Accepts either:
      - {'exported_in': [...], 'imported_in': [...]}
      - [ {exported_in: [...], imported_in: [...]}, 'path', ... ]
    Returns (exported_in, imported_in) with duplicates removed (order-stable).
    """
    exported_in, imported_in = [], []
    if isinstance(data, dict):
        exported_in = list(dict.fromkeys(data.get('exported_in', [])))
        imported_in = list(dict.fromkeys(data.get('imported_in', [])))
    elif isinstance(data, list):
        for d in data:
            if isinstance(d, dict):
                exported_in += d.get('exported_in', [])
                imported_in += d.get('imported_in', [])
            elif isinstance(d, str):
                exported_in.append(d); imported_in.append(d)
        exported_in = list(dict.fromkeys(exported_in))
        imported_in = list(dict.fromkeys(imported_in))
    return exported_in, imported_in

def _render_symbol_lists_for(self, name: str, mapping: dict,
                             exporters_widget, importers_widget,
                             mode: str = "io"):
    """
    Generic renderer for functions/variables.
    mode: "source" -> only exporters
          "io"     -> exporters + importers
          "all"    -> union shown in exporters_widget
    """
    exporters_widget.clear()
    if importers_widget is not None:
        importers_widget.clear()

    data = mapping.get(name, {'exported_in': [], 'imported_in': []})
    exported_in, imported_in = _normalize_map_entry(data)

    if mode == "source":
        for f in sorted(exported_in):
            exporters_widget.addItem(f)
    elif mode == "io":
        for f in sorted(exported_in):
            exporters_widget.addItem(f)
        if importers_widget is not None:
            for f in sorted(imported_in):
                importers_widget.addItem(f)
    else:  # "all"
        union = sorted(set(exported_in) | set(imported_in))
        for f in union:
            exporters_widget.addItem(f)

# --- variables: mirror functions with tiny wrapper(s) -------------------------
# If you have SEPARATE list widgets for variables:
def _on_var_filter_mode_changed(self):
    self.var_filter_mode = "source" if self.rb_var_source.isChecked() else ("all" if self.rb_var_all.isChecked() else "io")
    if getattr(self, "current_var", None):
        self._render_var_lists_for(self.current_var)

# functionsTab/functionsTab/functions/variable_filter_utils.py
def _render_var_lists_for(self, var_name: str):
    _render_symbol_lists_for(
        self, var_name, self.var_map,
        self.exporters_list, self.importers_list,
        getattr(self, "var_filter_mode", getattr(self, "fn_filter_mode", "io"))
    )
def _on_var_map_ready(self, var_map: dict):
    self.var_map = var_map or {}
