from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (
    QHBoxLayout, QPushButton, QFileDialog, QMenu, QMessageBox, QListWidgetItem
)
from PyQt6.QtGui import QKeySequence, QShortcut, QFont
from PyQt6.QtCore import Qt
from ..imports import *
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QFileDialog, QMenu, QMessageBox
from PyQt6.QtGui import QKeySequence, QShortcut, QFont
from PyQt6.QtCore import Qt

def wire_map_copy_ui(self):
    # Buttons
    row = QHBoxLayout()
    self.btn_copy_sel = QPushButton("Copy Selected")
    self.btn_copy_all = QPushButton("Copy All")
    self.btn_save_map  = QPushButton("Save…")
    row.addWidget(self.btn_copy_sel)
    row.addWidget(self.btn_copy_all)
    row.addWidget(self.btn_save_map)
    row.addStretch(1)
    self.layout().addLayout(row)

    self.btn_copy_sel.clicked.connect(lambda: copy_map(self, only_selected=True))
    self.btn_copy_all.clicked.connect(lambda: copy_map(self, only_selected=False))
    self.btn_save_map.clicked.connect(lambda: save_map_to_file(self))

    # Shortcuts (PyQt6)
    copy_seq = QKeySequence(QKeySequence.StandardKey.Copy)           # maps to Cmd+C on macOS
    QShortcut(copy_seq, self.list, activated=lambda: copy_map(self, only_selected=True))
    QShortcut(QKeySequence("Ctrl+Shift+C"), self, activated=lambda: copy_map(self, only_selected=False))

    # Context menu
    self.list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    self.list.customContextMenuRequested.connect(lambda pos: _map_context_menu(self, pos))

    # Optional: monospace font for pretty maps
    f = self.list.font()
    f.setStyleHint(QFont.StyleHint.TypeWriter)
    self.list.setFont(f)

def _gather_map_text(self, only_selected: bool) -> str:
    items = self.list.selectedItems() if only_selected else [self.list.item(i) for i in range(self.list.count())]
    return "\n".join(i.text() for i in items if i is not None)

def copy_map(self, only_selected: bool = False) -> None:
    text = _gather_map_text(self, only_selected)
    if not text:
        QMessageBox.information(self, "Copy Map", "Nothing to copy.")
        return
    QtWidgets.QApplication.clipboard().setText(text)
    if hasattr(self, "append_log"):
        self.append_log(f"📋 Copied {len(text.splitlines())} line(s) to clipboard.\n")

def save_map_to_file(self) -> None:
    text = _gather_map_text(self, only_selected=False)
    if not text:
        QMessageBox.information(self, "Save Map", "Nothing to save.")
        return
    fn, _ = QFileDialog.getSaveFileName(self, "Save Directory Map", "directory_map.txt",
                                        "Text Files (*.txt);;All Files (*)")
    if not fn:
        return
    try:
        with open(fn, "w", encoding="utf-8") as f:
            if not text.endswith("\n"): text += "\n"
            f.write(text)
        if hasattr(self, "append_log"):
            self.append_log(f"💾 Saved map to {fn}\n")
    except Exception as e:
        QMessageBox.critical(self, "Save failed", str(e))

def _map_context_menu(self, pos: QtCore.QPoint) -> None:
    menu = QMenu(self.list)
    a_copy     = menu.addAction("Copy")
    a_copy_all = menu.addAction("Copy All")
    a_save     = menu.addAction("Save…")
    act = menu.exec(self.list.viewport().mapToGlobal(pos))
    if act == a_copy:     copy_map(self, True)
    elif act == a_copy_all: copy_map(self, False)
    elif act == a_save:   save_map_to_file(self)
def start_map(self):
    self.btn_run.setEnabled(False)
    try:
        self.params = make_params(self)
    except Exception as e:
        QMessageBox.critical(self, "Bad input", str(e))
        self.btn_run.setEnabled(True)
        return

    class MapWorker(QThread):
        log = pyqtSignal(str)
        done = pyqtSignal(list)   # emit list of results instead of plain str

        def __init__(self, params):
            super().__init__()
            self.params = params

        def run(self):
            try:
                # assume get_directory_map returns str -> split into lines
                map_str = get_directory_map(**self.params)
                results = [line for line in map_str.splitlines() if line.strip()]
                self.done.emit(results)
            except Exception:
                tb = traceback.format_exc()
                self.log.emit(tb)
                self.done.emit([])

    self.worker = MapWorker(self.params)
    self.worker.log.connect(self.append_log)      # errors → logs
    self.worker.done.connect(self.display_map)    # results → results list
    self.worker.finished.connect(lambda: self.btn_run.setEnabled(True))
    self.worker.start()


def append_log(self, text: str):
    """Append error/debug text into logs pane."""
    self.log.moveCursor(self.log.textCursor().MoveOperation.End)
    self.log.insertPlainText(text)
    self.log.ensureCursorVisible()


def display_map(self, results: list[str]):
    """Display map results in the Results list widget."""
    self.list.clear()
    if results:
        self.list.addItems(results)
    else:
        self.append_log("No map generated.\n")
