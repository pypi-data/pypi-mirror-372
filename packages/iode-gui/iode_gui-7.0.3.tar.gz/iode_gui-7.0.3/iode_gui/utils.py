from PySide6.QtCore import Qt, QUrl, QDir, QLocale

import iode_gui.iode_resource_rc
from iode_gui import DOC_DIR as GUI_DOC_DIR
from iode import DOC_DIR

IODE_VERSION = "IODE Modeling Software 7.0.3 - (c) 1990-2025 Federal Planning Bureau - Brussels"
IODE_VERSION_MAJOR = 7
IODE_VERSION_MINOR = 0
IODE_VERSION_PATCH = 3

ORGANIZATION_NAME = "Federal Planning Bureau (Belgium)"

QLocale.setDefault(QLocale("C"))

NAN_REP = "--"
MAX_PRECISION_NUMBERS = 10
DEFAULT_FONT_FAMILY = "Consolas, \"Courier New\", monospace"
SHOW_IN_TEXT_TAB_EXTENSIONS_LIST = (".txt", ".a2m", ".prf", ".dif", ".asc", ".ref")
IODE_REPORT_EXTENSION = ".rep"
TMP_FILENAME: str =  "~dummy"

URL_HOMEPAGE = QUrl("https://iode.readthedocs.io/en/stable/")
URL_CHANGELOG = QUrl("https://iode.readthedocs.io/en/stable/changes.html")
URL_PYTHON_API = QUrl("https://iode.readthedocs.io/en/stable/api.html")

URL_MANUAL = QUrl.fromLocalFile(DOC_DIR + "/iode.chm")
URL_SHORTCUTS = QUrl.fromLocalFile(GUI_DOC_DIR + "/keyboard_shortcuts.pdf")


class Context:
    """Context class to store the context of the application"""
    called_from_python_script: bool = False

    def __init__(self) -> None:
        raise NotImplementedError()

    @classmethod
    def set_called_from_python_script(cls, called_from_python_script: bool) -> None:
       cls.called_from_python_script = called_from_python_script
