from ..imports import *
from .initFuncs import initFuncs
# New Tab: Directory Map
class directoryMapTab(QWidget):
    def __init__(self, bus: SharedStateBus):
        super().__init__()
        self.setLayout(QVBoxLayout())
        grid = QGridLayout()
        install_common_inputs(
            self, grid, bus=bus,
            primary_btn=("Get Directory Map", self.start_map)
        )

        # Layout form
        # Prefix
        self.prefix_in = QLineEdit("")
        self.prefix_in.setPlaceholderText("Optional prefix")
        # Flags
        self.chk_recursive = QCheckBox("Recursive"); self.chk_recursive.setChecked(True)
        self.chk_include_files = QCheckBox("Include Files"); self.chk_include_files.setChecked(True)
        self.chk_add = QCheckBox("Add to defaults"); self.chk_add.setChecked(False)
        # Run
        self.btn_run = QPushButton("Get Directory Map")
        self.btn_run.clicked.connect(self.start_map)
        # Output area
   
        self.layout().addWidget(QLabel("Results"))
        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self.start_map)
        self.layout().addWidget(self.list, stretch=3)
        self._last_results = []
directoryMapTab = initFuncs(directoryMapTab)
