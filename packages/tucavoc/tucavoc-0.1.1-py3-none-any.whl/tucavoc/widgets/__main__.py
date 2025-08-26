import logging
import sys
from PySide6.QtWidgets import QApplication

from tucavoc.widgets.main import TucavocWidget

if __name__ == "__main__":
    app = QApplication([])

    logging.basicConfig(level=logging.INFO)

    widget = TucavocWidget()
    widget.show()

    sys.exit(app.exec())
