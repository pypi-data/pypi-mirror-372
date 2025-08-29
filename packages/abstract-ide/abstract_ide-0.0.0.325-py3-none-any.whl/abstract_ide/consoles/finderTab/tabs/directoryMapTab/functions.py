from ..imports import *

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
