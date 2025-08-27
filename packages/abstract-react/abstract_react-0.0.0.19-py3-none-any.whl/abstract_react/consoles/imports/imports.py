from __future__ import annotations
import re
from typing import List, Dict, Any, Tuple
from abstract_gui.QT6 import QStackedWidget, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView, QButtonGroup
from abstract_gui.QT6.imports import *
from pathlib import Path
from ...react_analyzer import *
class ImportGraphWorker(QThread):
    log = pyqtSignal(str)
    ready = pyqtSignal(dict, dict)

    def __init__(self, project_root: str, scope: str = 'all', entries=None):
        super().__init__()
        self.project_root = project_root
        self.scope = scope
        self.entries = entries or ["index", "main"]  # GUI can override

    def run(self):
        try:
            root = Path(self.project_root).resolve()
            self.log.emit(f"[map] scanning {root} (scope={self.scope})\n")
            if self.scope == "reachable":
                entry = find_entry(root, self.entries)
                self.log.emit(f"[map] entry={entry}\n")
                graph = build_graph_reachable(entry, root)
            else:
                graph = build_graph_all(root)

            func_map = invert_to_function_map(graph)
            self.log.emit(f"[map] files={len(graph['nodes'])} edges={len(graph['edges'])} functions={len(func_map)}\n")
            self.ready.emit(graph, func_map)
        except Exception as e:
            self.log.emit(f"[map] error: {e}\n{traceback.format_exc()}\n")
            self.ready.emit({}, {})

def start_work(self):
    try:
        self.run_btn.setEnabled(False)
        user = self.user_in.text().strip() or 'solcatcher'   # <- swap order (yours hard-coded the default)
        path = self.path_in.text().strip()
        if not path or not os.path.isdir(path):
            QMessageBox.critical(self, "Error", "Invalid project path.")
            self.run_btn.setEnabled(True)
            return

        # Clear old UI bits
        self.errors_list.clear()
        self.warnings_list.clear()

        # Kick off non-blocking build
        self._run_build_qprocess(path)

    except Exception:
        self.append_log("start_work error:\n" + traceback.format_exc() + "\n")
        self.run_btn.setEnabled(True)

def clear_ui(self):
    self.log_view.clear()
    self.errors_list.clear()
    self.warnings_list.clear()
    self.last_output = ""
    self.last_errors_only = ""
    self.last_warnings_only = ""
