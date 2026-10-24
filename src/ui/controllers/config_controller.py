from PyQt6.QtCore import QObject, pyqtSignal

from ui.windows.config_window import ConfigWindow
from data_structure.app_config import config, LANGUAGES, FONT_RANGE
from ui.theme import THEMES, theme_manager

class ConfigController(QObject):
    changed = pyqtSignal()          # emitted after new preferences were saved

    
    

    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self.config = config
        self.storage = storage
        self._window = None

    def open(self, parent_widget=None):
        if self._window is not None:             # already open: just bring it forward
            self._window.raise_()
            self._window.activateWindow()
            return

        window = ConfigWindow(THEMES, LANGUAGES, FONT_RANGE,
                              parent_widget)
        window.set_values(self.config.theme, self.config.font_size,
                          self.config.app_language)
        window.apply_requested.connect(self.apply)
        window.finished.connect(self._on_closed)
        self._window = window
        window.open()                            # modal, but doesn't block this call

    def _on_closed(self):
        self._window.deleteLater()
        self._window = None

    def apply(self, values):
        theme = values["theme"]
        language = values["app_language"]
        size = max(FONT_RANGE[0], min(FONT_RANGE[1], int(values["font_size"])))

        if theme not in THEMES or language not in LANGUAGES:
            return                               # ignore invalid input

        unchanged = (theme == self.config.theme
                     and size == self.config.font_size
                     and language == self.config.app_language)
        if unchanged:
            return

        self.config.theme = theme
        theme_manager.set_theme(theme)  # apply immediately
        self.config.font_size = size
        self.config.app_language = language
        self.storage.save_config_data(self.config.get_data())
        self.changed.emit()