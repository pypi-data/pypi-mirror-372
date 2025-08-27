from .initFuncs import initFuncs
from typing import *
from abstract_gui.QT6 import *
from abstract_utilities import get_logFile
from .imports import *
logger = get_logFile(__name__)
# ─── Main GUI ─────────────────────────────────────────────────────────────
class apiTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("API Console for abstract_apis")
        self.api_prefix = "/api" # default; will update on detect or user edit
        self.resize(800, 900)
        self.config_cache = {} # cache per-endpoint settings
        self._build_ui()

     
apiTab = initFuncs(apiTab)
