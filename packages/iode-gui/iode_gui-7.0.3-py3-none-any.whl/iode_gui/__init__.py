from pathlib import Path

__version__ = "7.0.3"

DOC_DIR = str((Path(__file__).parent / "doc").resolve())

from iode_gui.main import start, open_application
