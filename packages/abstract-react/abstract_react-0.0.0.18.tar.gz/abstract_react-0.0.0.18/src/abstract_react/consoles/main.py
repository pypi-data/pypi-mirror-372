from .functionsTab import _FunctionsTab
from .runnerTab import runnerTab
from abstract_gui import startConsole
from abstract_gui.QT6 import ConsoleBase, QTabWidget,install_qt_logging, add_logs_tab, add_logs_to   # << add
# Content Finder = the nested group you built (Find Content, Directory Map, Collect, Imports, Diff)
class reactRunnerConsole(ConsoleBase):
    def __init__(self, *, bus=None, parent=None):
        super().__init__(bus=bus, parent=parent)
        inner = QTabWidget()
        self.layout().addWidget(inner)
        install_qt_logging() 
        # all content tabs share THIS console’s bus
        inner.addTab(runnerTab(),      "react Runner")
        inner.addTab(_FunctionsTab(),   "Functions")
        add_logs_tab(inner, title="Logs")   # << auto-attaches to the same logger pipe
        self._logs_view = add_logs_to(self)   # adds a Show/Hide Logs bar + panel

def startReactRunnerConsole():
    startConsole(reactRunnerConsole)
