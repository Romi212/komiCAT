from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QFormLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QVBoxLayout,
)


class ConfigWindow(QDialog):
    # {"theme": code, "font_size": int, "app_language": code}
    apply_requested = pyqtSignal(dict)

    def __init__(self, themes, languages, font_range, parent=None):
        """themes / languages: {code: display name}. font_range: (min, max)."""
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setModal(True)

        root = QVBoxLayout(self)
        root.setSpacing(16)

        # ---- title with gear ----
        title = QLabel("⚙  Preferences")
        title.setObjectName("preferencesTitle")
        root.addWidget(title)

        # ---- form ----
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.theme_combo = QComboBox()
        for name in themes:                      # iterating a dict gives the keys: "Dark", "Light"
            self.theme_combo.addItem(name, name)

        self.font_spin = QSpinBox()
        self.font_spin.setRange(*font_range)

        self.language_combo = QComboBox()
        for code, name in languages.items():
            self.language_combo.addItem(name, code)

        form.addRow("Color theme", self.theme_combo)
        form.addRow("Font size", self.font_spin)
        form.addRow("App language", self.language_combo)
        root.addLayout(form)

        # ---- buttons ----
        buttons = QHBoxLayout()
        self.cancel_btn = QPushButton("Cancel")
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setDefault(True)
        self.cancel_btn.clicked.connect(self.reject)
        self.apply_btn.clicked.connect(self._on_apply)
        buttons.addStretch()
        buttons.addWidget(self.cancel_btn)
        buttons.addWidget(self.apply_btn)
        buttons.addStretch()
        root.addLayout(buttons)

    def set_values(self, theme, font_size, language):
        self._select(self.theme_combo, theme)
        self.font_spin.setValue(font_size)
        self._select(self.language_combo, language)

    @staticmethod
    def _select(combo, code):
        idx = combo.findData(code)
        if idx >= 0:                      # unknown code: leave the first item selected
            combo.setCurrentIndex(idx)

    def _on_apply(self):
        self.apply_requested.emit({
            "theme": self.theme_combo.currentData(),
            "font_size": self.font_spin.value(),
            "app_language": self.language_combo.currentData(),
        })
        self.accept()