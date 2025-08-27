import traceback
from pathlib import Path
from abstract_gui.QT6.imports import QThread,pyqtSignal
from .invert_utils import invert_to_function_map,invert_to_variable_map
from .graph_utils import build_graph_all,build_graph_reachable
from .utils import find_entry
class ImportGraphWorker(QThread):
    log = pyqtSignal(str)
    ready = pyqtSignal(dict, dict, dict)

    def __init__(self,
                 project_root: str,
                 scope: str = 'all',
                 entries=None
                 ):
        super().__init__()
        self.project_root = project_root
        self.root = Path(self.project_root).resolve()
        self.scope = scope
        self.entries = entries or ["index", "main"]  # GUI can override
        
        self.graph = self.get_graph()
        self.func_map = invert_to_function_map(self.graph)
        self.var_map  = invert_to_variable_map(self.graph)
        
    def run(self):
        try:
            root = Path(self.project_root).resolve()
            self.log.emit(f"[map] scanning {root} (scope={self.scope})\n")
            self.graph = self.get_graph()
            self.func_map = invert_to_function_map(self.graph)
            self.var_map  = invert_to_variable_map(self.graph)
            self.log.emit(
                f"[map] files={len(graph['nodes'])} edges={len(graph['edges'])} "
                f"functions={len(func_map)} vars={len(var_map)}\n"
            )
            self.ready.emit(self.graph, self.func_map, self.var_map)
        except Exception as e:
            self.log.emit(f"[map] error: {e}\n{traceback.format_exc()}\n")
            self.ready.emit({}, {}, {})
    def get_graph(self):
        if self.scope == "reachable":
            self.entry = find_entry(self.root, self.entries)
            self.log.emit(f"[map] entry={self.entry}\n")
            self.graph = build_graph_reachable(self.entry, self.root)
        else:
            self.graph = build_graph_all(self.root)
        return self.graph
