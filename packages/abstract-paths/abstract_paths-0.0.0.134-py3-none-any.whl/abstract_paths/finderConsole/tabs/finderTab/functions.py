from ..imports import *
import os
# — UI helpers —
def enable_widget(parent, name: str, enabled: bool):
    try:
        getattr(parent, name).setEnabled(enabled)
    except AttributeError:
        print(f"[WARN] No widget {name} in {parent}")

# — Actions —
def start_search(self):
 
    enable_widget(self,"btn_run",False)
    try:
        params = make_params(self)
    except Exception as e:
        QMessageBox.critical(self, "Bad input", str(e))

        enable_widget(self,"btn_run",True)
        return
    self.worker = SearchWorker(params)
    self.worker.log.connect(self.append_log)
    self.worker.done.connect(self.populate_results)
    self.worker.finished.connect(lambda: enable_widget(self,"btn_run",True))
    self.worker.start()
def append_log(self, text: str):
    self.log.moveCursor(self.log.textCursor().MoveOperation.End)
    self.log.insertPlainText(text)

def populate_results(self, results: list):
    self._last_results = results or []
    if not results:
        self.append_log("✅ No matches found.\n")
        enable_widget(self, "btn_secondary", False)
        return

    self.append_log(f"✅ Found {len(results)} file(s).\n")
    enable_widget(self, "btn_secondary", True)

    for fp in results:
        if isinstance(fp, dict):
            file_path = fp.get("file_path")
            lines = fp.get("lines", [])
        else:
            file_path = fp
            lines = []

        if not isinstance(file_path, str):
            continue

        if lines:
            for obj in lines:
                line = obj.get("line")
                text = f"{file_path}:{line}" if line is not None else file_path
                item = QListWidgetItem(text)
                item.setData(Qt.ItemDataRole.UserRole, {"file_path": file_path, "line": line})
                self.list.addItem(item)
                self.append_log(text + "\n")
        else:
            item = QListWidgetItem(file_path)
            item.setData(Qt.ItemDataRole.UserRole, {"file_path": file_path, "line": None})
            self.list.addItem(item)
            self.append_log(file_path + "\n")
