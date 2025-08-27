from PyQt6.QtWidgets import QGridLayout,QWidget,QCheckBox,QLineEdit,QPushButton,QLabel
from PyQt6.QtCore import QSignalBlocker
from ..methods import visibilityMgr
from PyQt6.QtCore import QObject, pyqtSignal
from .results import *
from .states import *
class SharedStateBus(QObject):
    stateBroadcast = pyqtSignal(object, dict)  # (sender, state)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._snap: dict = {}

    def snapshot(self) -> dict:
        return dict(self._snap)

    def push(self, sender, state: dict):
        self._snap = dict(state)
        self.stateBroadcast.emit(sender, self.snapshot())
def install_common_inputs(host, grid: QGridLayout, *,
                          bus: SharedStateBus,
                          primary_btn=("Run", None),
                          secondary_btn=("Secondary", None),
                          default_allowed_exts_in="ts,tsx,js,jsx,css",
                          default_unallowed_exts_in="",
                          default_exclude_types_in="",
                          default_exclude_dirs_in=['__pycache__','node_modules','junk','backs','backups','backup','logs'],
                          default_exclude_patterns_in="",
                          # NEW:
                          auto_unlink_on_init_if_diff=True,
                          global_default_filters: dict | None = None):

    """
    Adds the shared controls to `host` and wires them to `bus`.
    Expects `host` to already have a QVBoxLayout() as its layout().
    """
    host._bus = bus
    host._applying_remote = False
    host._input_grid = grid
    form_container = QWidget()
    form_container.setLayout(grid)
    host._input_container = form_container
    host.browse_dir = browse_dir
    host.make_params = make_params
    # --- widgets (your exact fields) -------------------------------------
    host.dir_in = QLineEdit(os.getcwd())
    btn_browse = QPushButton("Browse…")
    btn_browse.clicked.connect(lambda: _browse_dir(host))
    host._vis = visibilityMgr(host, settings_app="common_inputs", animate_default=True)
    host.strings_in = QLineEdit("")
    host.strings_in.setPlaceholderText("comma,separated,strings")

    host.allowed_exts_in   = QLineEdit(make_string(default_allowed_exts_in or ""))
    host.unallowed_exts_in = QLineEdit(make_string(default_unallowed_exts_in or ""))
    host.exclude_types_in  = QLineEdit(make_string(default_exclude_types_in or ""))
    host.exclude_dirs_in   = QLineEdit(make_string(default_exclude_dirs_in or ""))
    host.exclude_patterns_in = QLineEdit(make_string(default_exclude_patterns_in or ""))

    host.chk_add        = QCheckBox("Add");          host.chk_add.setChecked(False)
    host.chk_recursive  = QCheckBox("Recursive");    host.chk_recursive.setChecked(True)
    host.chk_total      = QCheckBox("Require ALL strings (total_strings)")
    host.chk_total.setChecked(False)
    host.chk_parse      = QCheckBox("parse_lines");  host.chk_parse.setChecked(False)
    host.chk_getlines   = QCheckBox("get_lines");    host.chk_getlines.setChecked(True)

    host.spec_spin = QSpinBox(); host.spec_spin.setRange(0, 999999); host.spec_spin.setValue(0)


    # toolbar row you already have
    link_row = QHBoxLayout()
    host.link_btn = QToolButton(); host.link_btn.setCheckable(True); host.link_btn.setChecked(True)
    host.link_btn.setText("🔗 Linked"); link_row.addWidget(host.link_btn)
    link_row.addStretch(1)
    host.layout().addLayout(link_row)

    # NEW: visibility manager
    if not hasattr(host, "_vis"):
        host._vis = VisibilityMgr(host, settings_app="FinderConsole", animate_default=True)

    # Register the form as a collapsible section, auto-create a toggle button and place it in link_row
    host._vis.collapse_btn = host._vis.register(
        name="filters",
        container=form_container,
        button_host_layout=link_row,          # puts the button next to "Linked" control
        start_visible=True,
        animate=True,                         # slide animation
        shortcut="Ctrl+`",                    # toggle with a hotkey
        button_text_open="−",
        button_text_closed="+",
        persist=True
    )
    # --- lay out form -----------------------------------------------------
    r = 0
    grid.addWidget(QLabel("Directory"), r, 0); grid.addWidget(host.dir_in, r, 1); grid.addWidget(btn_browse, r, 2); r+=1
    grid.addWidget(QLabel("Strings"), r, 0); grid.addWidget(host.strings_in, r, 1, 1, 2); r+=1
    grid.addWidget(QLabel("Allowed Exts"), r, 0); grid.addWidget(host.allowed_exts_in, r, 1, 1, 2); r+=1
    grid.addWidget(QLabel("Unallowed Exts"), r, 0); grid.addWidget(host.unallowed_exts_in, r, 1, 1, 2); r+=1
    grid.addWidget(QLabel("Exclude Types"), r, 0); grid.addWidget(host.exclude_types_in, r, 1, 1, 2); r+=1
    grid.addWidget(QLabel("Exclude Dirs"), r, 0); grid.addWidget(host.exclude_dirs_in, r, 1, 1, 2); r+=1
    grid.addWidget(QLabel("Exclude Patterns"), r, 0); grid.addWidget(host.exclude_patterns_in, r, 1, 1, 2); r+=1

    flags = QHBoxLayout()
    for w in (host.chk_recursive, host.chk_total, host.chk_parse, host.chk_getlines, host.chk_add):
        flags.addWidget(w)
    grid.addLayout(flags, r, 0, 1, 3); r+=1

    sp = QHBoxLayout()
    sp.addWidget(QLabel("spec_line (0=off):")); sp.addWidget(host.spec_spin); sp.addStretch(1)
    grid.addLayout(sp, r, 0, 1, 3); r+=1

    host.layout().addWidget(form_container)
    # Register the form as a collapsible section, auto-create a toggle button and place it in link_row

    host.layout().addWidget(form_container)
    # CTA row
    cta = QHBoxLayout()
    if primary_btn[1]:
        host.btn_run = QPushButton(primary_btn[0]); host.btn_run.clicked.connect(primary_btn[1])
        cta.addWidget(host.btn_run)
    cta.addStretch(1)
    if secondary_btn[1]:
        host.btn_secondary = QPushButton(secondary_btn[0]); host.btn_secondary.clicked.connect(secondary_btn[1])
        cta.addWidget(host.btn_secondary)
    host.layout().addLayout(cta)
    
    # --- wiring: local changes → bus when linked --------------------------
    def maybe_broadcast(*_):
        if not host.link_btn.isChecked() or host._applying_remote:
            return
        bus.push(host, _read_state(host))

    for le in (host.dir_in, host.strings_in, host.allowed_exts_in,
               host.unallowed_exts_in, host.exclude_types_in,
               host.exclude_dirs_in, host.exclude_patterns_in):
        le.textEdited.connect(maybe_broadcast)

    for cb in (host.chk_add, host.chk_recursive, host.chk_total, host.chk_parse, host.chk_getlines):
        cb.toggled.connect(maybe_broadcast)

    host.spec_spin.valueChanged.connect(maybe_broadcast)

    # bus → host (apply shared state when linked)
    def apply_shared(sender, state: dict):
        if sender is host or not host.link_btn.isChecked():
            return
        _write_state(host, state)
    bus.stateBroadcast.connect(apply_shared)

    # ---------------- initial sync + one-time auto-unlink -----------------
    current = _read_state(host)
    snap = bus.snapshot()

    # Build a comparison baseline if caller didn't pass one
    if global_default_filters is None:
        global_default_filters = dict(
            allowed_exts     = default_allowed_exts_in,
            unallowed_exts   = default_unallowed_exts_in,
            exclude_types    = default_exclude_types_in,
            exclude_dirs     = default_exclude_dirs_in,
            exclude_patterns = default_exclude_patterns_in,
        )

    # If a snapshot exists, compare to it; else compare to declared defaults
    compare_to = snap if snap else global_default_filters

    if auto_unlink_on_init_if_diff and _filters_subset(current) != _filters_subset(compare_to):
        # Filters differ → start Independent (only on init)
        with QSignalBlocker(host.link_btn):
            host.link_btn.setChecked(False)
            host.link_btn.setText("⛓ Independent")
        # Do NOT push/pull now; leave this tab’s values as-is and independent.
    else:
        # Same filters → remain Linked and sync with the bus/defaults
        if snap:
            _write_state(host, snap)      # pull bus
        else:
            bus.push(host, current)       # seed bus
