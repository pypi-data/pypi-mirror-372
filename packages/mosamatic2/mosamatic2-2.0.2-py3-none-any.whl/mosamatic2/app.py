import sys
import traceback
import mosamatic2.constants as constants
from PySide6 import QtWidgets
from mosamatic2.ui.settings import Settings
from mosamatic2.core.managers.logmanager import LogManager
from mosamatic2.ui.widgets.splashscreen import SplashScreen

LOG = LogManager()


def main():
    settings = Settings()
    application_name = settings.get(constants.MOSAMATIC2_WINDOW_TITLE)
    QtWidgets.QApplication.setApplicationName(application_name)
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(application_name)
    try:
        splash = SplashScreen()
        splash.show()
        sys.exit(app.exec())
    except Exception as e:
        LOG.error(str(e))
        LOG.error(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    main()