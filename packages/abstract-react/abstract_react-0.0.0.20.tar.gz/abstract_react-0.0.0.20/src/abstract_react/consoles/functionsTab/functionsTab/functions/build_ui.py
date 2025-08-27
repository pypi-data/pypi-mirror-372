# functionsTab/functionsTab/functions/build_ui.py
from ..imports import *
from abstract_gui.QT6 import attach_textedit_to_logs

def _build_ui(self, use_flow: bool=True):
    root = QHBoxLayout(self)

    # ---------- left panel (project/scan + tabs) ----------
    left = QVBoxLayout()

    # project row (unchanged)
    row = QHBoxLayout()
    row.addWidget(QLabel("Project Path:"))
    self.path_in = QLineEdit(self.init_path)
    self.path_in.setPlaceholderText("Folder containing package.json / source")
    row.addWidget(self.path_in, 1)
    row.addWidget(QLabel("Scope:"))
    self.scope_combo = QComboBox(); self.scope_combo.addItems(["all", "reachable"])
    row.addWidget(self.scope_combo)
    left.addLayout(row)

    self.btn_scan = QPushButton("Scan Project")
    left.addWidget(self.btn_scan)

    # ---- NEW: tabs for Functions / Variables chips -----------------
    self.tabs = QTabWidget()

    # --- Functions tab
    self.fn_tab = QWidget(); fn_v = QVBoxLayout(self.fn_tab)

    self.search_fn = QLineEdit(); self.search_fn.setPlaceholderText("Filter functions…")
    fn_v.addWidget(self.search_fn)

    self.rb_fn_source = QRadioButton("Function")
    self.rb_fn_io     = QRadioButton("Import/Export"); self.rb_fn_io.setChecked(True)
    self.rb_fn_all    = QRadioButton("All")
    self.fn_filter_group = QButtonGroup(self)
    for rb in (self.rb_fn_source, self.rb_fn_io, self.rb_fn_all):
        self.fn_filter_group.addButton(rb); fn_v.addWidget(rb)

    self.fn_scroll = QScrollArea(); self.fn_scroll.setWidgetResizable(True)
    self.fn_container = QWidget()
    if use_flow:
        self.fn_layout = flowLayout(self.fn_container, hspacing=8, vspacing=6)
        self.fn_container.setLayout(self.fn_layout)
    else:
        box = QVBoxLayout(self.fn_container)
        box.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.fn_layout = box
    self.fn_scroll.setWidget(self.fn_container)
    fn_v.addWidget(self.fn_scroll)

    # --- Variables tab
    self.var_tab = QWidget(); var_v = QVBoxLayout(self.var_tab)

    self.search_var = QLineEdit(); self.search_var.setPlaceholderText("Filter variables…")
    var_v.addWidget(self.search_var)

    self.rb_var_source = QRadioButton("Variable")
    self.rb_var_io     = QRadioButton("Import/Export"); self.rb_var_io.setChecked(True)
    self.rb_var_all    = QRadioButton("All")
    self.var_filter_group = QButtonGroup(self)
    for rb in (self.rb_var_source, self.rb_var_io, self.rb_var_all):
        self.var_filter_group.addButton(rb); var_v.addWidget(rb)

    self.var_scroll = QScrollArea(); self.var_scroll.setWidgetResizable(True)
    self.var_container = QWidget()
    if use_flow:
        self.var_layout = flowLayout(self.var_container, hspacing=8, vspacing=6)
        self.var_container.setLayout(self.var_layout)
    else:
        vbox = QVBoxLayout(self.var_container)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.var_layout = vbox
    self.var_scroll.setWidget(self.var_container)
    var_v.addWidget(self.var_scroll)

    self.tabs.addTab(self.fn_tab,  "Functions")
    self.tabs.addTab(self.var_tab, "Variables")
    left.addWidget(self.tabs)

    # ---------- right panel (reuse for both kinds) ----------
    right = QVBoxLayout()
    right.addWidget(QLabel("Exported In"))
    self.exporters_list = QListWidget(); right.addWidget(self.exporters_list)
    right.addWidget(QLabel("Imported In"))
    self.importers_list = QListWidget(); right.addWidget(self.importers_list)
    right.addWidget(QLabel("Log"))
    self.log_view = QTextEdit(); self.log_view.setReadOnly(True); right.addWidget(self.log_view)
    try:
        attach_textedit_to_logs(self.log_view, tail_file=None)
    except Exception:
        pass

    root.addLayout(left, 1)
    root.addLayout(right, 2)

    # ---------- wiring ----------
    self.btn_scan.clicked.connect(lambda: self.scanRequested.emit(self.scope_combo.currentText()))
    self.scanRequested.connect(self._start_func_scan)

    # functions
    self.search_fn.textChanged.connect(self._filter_fn_buttons)
    self.rb_fn_source.toggled.connect(lambda _: self._on_filter_mode_changed())
    self.rb_fn_io.toggled.connect(    lambda _: self._on_filter_mode_changed())
    self.rb_fn_all.toggled.connect(   lambda _: self._on_filter_mode_changed())

    # variables
    self.search_var.textChanged.connect(self._filter_var_buttons)
    self.rb_var_source.toggled.connect(lambda _: self._on_var_filter_mode_changed())
    self.rb_var_io.toggled.connect(    lambda _: self._on_var_filter_mode_changed())
    self.rb_var_all.toggled.connect(   lambda _: self._on_var_filter_mode_changed())

    # optional: double-click open in editor
    self.exporters_list.itemDoubleClicked.connect(lambda it: os.system(f'code -g "{it.text()}"'))
    self.importers_list.itemDoubleClicked.connect(lambda it: os.system(f'code -g "{it.text()}"'))
