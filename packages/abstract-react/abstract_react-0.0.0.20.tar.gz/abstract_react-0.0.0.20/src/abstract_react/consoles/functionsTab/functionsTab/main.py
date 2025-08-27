# functions_console.py
from .imports import QWidget,pyqtSignal
from abstract_gui.QT6 import add_logs_to
from .initFuncs import initFuncs
# --- Console ---------------------------------------------------------------
# functionsTab/main.py

class functionsTab(QWidget):
    functionSelected = pyqtSignal(str)
    variableSelected = pyqtSignal(str)    # <- move here (don’t create signals inside __init__)
    scanRequested   = pyqtSignal(str)
    def __init__(self, parent=None, use_flow=False):
        super().__init__(parent)
        self.func_map = {}
        self.init_path= '/var/www/html/clownworld/bolshevid'
        self.fn_filter_mode = "io"
        self.current_fn = None
        self._build_ui(use_flow)
functionsTab = initFuncs(functionsTab)
