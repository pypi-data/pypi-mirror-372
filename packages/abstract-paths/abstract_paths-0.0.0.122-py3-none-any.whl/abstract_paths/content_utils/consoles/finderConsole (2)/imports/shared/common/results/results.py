from PyQt6.QtWidgets import QListWidgetItem
from .params import *
from ...robust_logger import get_log_file_path
def init_results_ui(self):
    # Wire helpers
    self.browse_dir = browse_dir

    self.make_params = make_params  # still returns dict of knobs (optional if you use _compute_files_from_self)

    # Log  Results UI
    
    self.layout().addWidget(QLabel("Results"))
    self.layout().addWidget(self.log, stretch=2)

    self.results_list = QListWidget()
    self.results_list.setUniformItemSizes(True)
    self.results_list.setSelectionMode(self.results_list.SelectionMode.ExtendedSelection)

    # bind as a free function with self
    self.results_list.itemDoubleClicked.connect(lambda it: _open_result(self, it))
    self.layout().addWidget(self.results_list, stretch=3)

    self._last_results = []
    attach_textedit_to_logs(self.log, tail_file=get_log_file_path())

    # Refresh when the shared bus broadcasts changes (and we’re linked)
    def _on_bus_change(sender, state):
        if getattr(self, "link_btn", None) and not self.link_btn.isChecked():
            return
        self._refresh_results()
    self._bus.stateBroadcast.connect(_on_bus_change)

    # Initial fill
    self._refresh_results()
    self = set_self_log(self)
    return self

def _open_result(self, item: QListWidgetItem):
    path = item.data(Qt.ItemDataRole.UserRole) or item.text()
    if not path:
        return
    QDesktopServices.openUrl(QUrl.fromLocalFile(path))

def _refresh_results(self):
    """Recompute the filtered files and (re)populate the list."""
    try:
        files = self.make_params()  # pulls from all current filters
    except Exception as e:
        if hasattr(self, "log"):
            self.log.append(f"Search failed: {e}\n")
        return

    self._last_results = files
    self.results_list.clear()

    for path in files:
        it = QListWidgetItem(path)  # show the path (or os.path.basename(path) if you prefer)
        it.setData(Qt.ItemDataRole.UserRole, path)  # keep full path
        self.results_list.addItem(it)

    if hasattr(self, "status_label"):
        n = len(files)
        self.status_label.setText(f"Found {n} file{'s' if n != 1 else ''}.")
        self.status_label.setStyleSheet("color: #2196f3;")  # blue
