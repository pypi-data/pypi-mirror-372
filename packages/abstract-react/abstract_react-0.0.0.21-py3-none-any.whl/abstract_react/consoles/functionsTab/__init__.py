import os
from abstract_gui import get_for_all_tabs
CONSOLE_DIR_PATH = os.path.abspath(__file__)
CONSOLE_ABS_DIR = os.path.dirname(CONSOLE_DIR_PATH)
get_for_all_tabs(CONSOLE_ABS_DIR)
from .main import _FunctionsTab,startFinderConsole


