# finderTab/functions.py
from ..imports import *
import os
from abstract_gui.QT6.utils.log_utils.robustLogger.searchWorker import SearchWorker  # be explicit

# — UI helpers —
def enable_widget(parent, name: str, enabled: bool):
    try:
        getattr(parent, name).setEnabled(enabled)
    except AttributeError:
        print(f"[WARN] No widget {name} in {parent}")

# — Actions —
def start_search(self):
    enable_widget(self, "btn_run", False)
    try:
        params = make_params(self)
    except Exception as e:
        QMessageBox.critical(self, "Bad input", str(e))
        enable_widget(self, "btn_run", True)
        return

    self.worker = SearchWorker(params)
    self.worker.log.connect(self.append_log)
    self.worker.done.connect(self.populate_results)
    # If SearchWorker is a QThread subclass:
    try:
        self.worker.finished.connect(lambda: enable_widget(self, "btn_run", True))
    except Exception:
        # If not a QThread, fall back to re-enabling in done
        self.worker.done.connect(lambda _=None: enable_widget(self, "btn_run", True))
    self.worker.start()

def append_log(self, text: str):
    """
    Append text to the tab's log widget (QPlainTextEdit or QTextEdit).
    Safe if self.log is missing.
    """
    edit = getattr(self, "log", None)

    # Prefer QPlainTextEdit (faster for logs)
    if isinstance(edit, QPlainTextEdit):
        if not text.endswith("\n"):
            text += "\n"
        edit.appendPlainText(text)
        return

    # QTextEdit fallback
    if isinstance(edit, QTextEdit):
        if not text.endswith("\n"):
            text += "\n"
        cursor = edit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
        edit.setTextCursor(cursor)
        edit.insertPlainText(text)
        return

    # No log widget? Avoid crashing, at least surface somewhere:
    try:
        print(text, end="" if text.endswith("\n") else "\n")
    except Exception:
        pass

def populate_results(self, results: list):
    self._last_results = results or []
    if not results:
        self.append_log("✅ No matches found.")
        enable_widget(self, "btn_secondary", False)
        return

    self.append_log(f"✅ Found {len(results)} file(s).")
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
                self.append_log(text)
        else:
            item = QListWidgetItem(file_path)
            item.setData(Qt.ItemDataRole.UserRole, {"file_path": file_path, "line": None})
            self.list.addItem(item)
            self.append_log(file_path)
