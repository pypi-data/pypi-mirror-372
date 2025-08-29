import os
import mosamatic2.constants as constants
from PySide6.QtWidgets import (
    QMainWindow,
)
from PySide6.QtGui import (
    QGuiApplication,
    QAction,
    QIcon,
)
from PySide6.QtCore import Qt, QByteArray
from mosamatic2.ui.utils import version, resource_path, is_macos
from mosamatic2.core.managers.logmanager import LogManager
from mosamatic2.ui.settings import Settings

LOG = LogManager()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self._settings = None
        self.init_window()

    def init_window(self):
        self.setWindowTitle(f'{constants.MOSAMATIC2_WINDOW_TITLE} {version()}')
        icon_file_name = constants.MOSAMATIC2_APP_ICON_FILE_NAME_MAC if is_macos() else constants.MOSAMATIC2_APP_ICON_FILE_NAME_WIN
        self.setWindowIcon(QIcon(resource_path(os.path.join(constants.MOSAMATIC2_ICONS_DIR_PATH, icon_file_name))))
        if not self.load_geometry_and_state():
            self.set_default_size_and_position()

    # GET

    def settings(self):
        if not self._settings:
            self._settings = Settings()
        return self._settings

    # MISCELLANEOUS

    def load_geometry_and_state(self):
        geometry = self.settings().get(constants.MOSAMATIC2_WINDOW_GEOMETRY_KEY)
        state = self.settings().get(constants.MOSAMATIC2_WINDOW_STATE_KEY)
        if isinstance(geometry, QByteArray) and self.restoreGeometry(geometry):
            if isinstance(state, QByteArray):
                self.restoreState(state)
            return True
        return False

    def save_geometry_and_state(self):
        self.settings().set(constants.MOSAMATIC2_WINDOW_GEOMETRY_KEY, self.saveGeometry())
        self.settings().set(constants.MOSAMATIC2_WINDOW_STATE_KEY, self.saveState())

    def set_default_size_and_position(self):
        self.resize(constants.MOSAMATIC2_WINDOW_W, constants.MOSAMATIC2_WINDOW_H)
        self.center_window()

    def center_window(self):
        screen = QGuiApplication.primaryScreen().geometry()
        x = (screen.width() - self.geometry().width()) / 2
        y = (screen.height() - self.geometry().height()) / 2
        self.move(int(x), int(y))