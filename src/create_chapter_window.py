from PyQt6.QtWidgets import (
    QCheckBox, QDialog, QDialogButtonBox, QFormLayout, QFrame, QLabel, QLineEdit,
    QSpinBox, QToolButton, QVBoxLayout
)
from PyQt6.QtCore import Qt


class CreateChapterWindow(QDialog):
    def __init__(self, parent=None, next_number=1, existing_numbers=None):
        super().__init__(parent)
        self.existing_numbers = set(existing_numbers)
        self.setWindowTitle("Add a new Chapter")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setMinimumWidth(340)

        main_layout = QVBoxLayout(self)

        # ---------- main fields ----------
        form = QFormLayout()
        self.number_input = QSpinBox()
        self.number_input.setRange(1, 9999)
        self.number_input.setValue(self._suggest_number())
        self.number_input.valueChanged.connect(self._validate)
        form.addRow("Chapter number:", self.number_input)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Optional, e.g. The Demon King")
        form.addRow("Chapter name:", self.name_input)

        

        self.warning_label = QLabel()
        self.warning_label.setObjectName("warningLabel")      # styled in build_qss
        self.warning_label.setWordWrap(True)
        self.warning_label.setVisible(False)
        main_layout.addWidget(self.warning_label)

        main_layout.addLayout(form)

        # ---------- advanced options (collapsed by default) ----------
        self.advanced_toggle = QToolButton()
        self.advanced_toggle.setText("Advanced options")
        self.advanced_toggle.setCheckable(True)
        self.advanced_toggle.setChecked(False)
        self.advanced_toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.advanced_toggle.setArrowType(Qt.ArrowType.RightArrow)
        self.advanced_toggle.setAutoRaise(True)
        self.advanced_toggle.toggled.connect(self._toggle_advanced)
        main_layout.addWidget(self.advanced_toggle)

        self.advanced_frame = QFrame()
        adv_layout = QVBoxLayout(self.advanced_frame)
        adv_layout.setContentsMargins(20, 0, 0, 0)
        self.use_termbase = QCheckBox("Use series termbase")
        self.use_termbase.setChecked(True)
        self.use_memory = QCheckBox("Use series translation memory")
        self.use_memory.setChecked(True)
        adv_layout.addWidget(self.use_termbase)
        adv_layout.addWidget(self.use_memory)
        self.advanced_frame.setVisible(False)
        main_layout.addWidget(self.advanced_frame)

        # ---------- OK / Cancel ----------
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.setCenterButtons(True)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self._validate()

    def _suggest_number(self):
        """Lowest free number after the highest existing one."""
        return max(self.existing_numbers, default=0) + 1

    def _validate(self):
        number = self.number_input.value()
        duplicate = number in self.existing_numbers
        self.warning_label.setVisible(duplicate)
        if duplicate:
            self.warning_label.setText(f"Chapter {number} already exists in this project.")
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(not duplicate)
        self.adjustSize()

    # ---------- behavior ----------
    def _toggle_advanced(self, expanded):
        self.advanced_frame.setVisible(expanded)
        self.advanced_toggle.setArrowType(
            Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow)
        self.adjustSize()                    # shrink or grow the dialog with the section

    def get_chapter_data(self):
        number = self.number_input.value()
        return {
            "number": number,
            "name": self.name_input.text().strip() or f"Chapter {number}",
            "use_series_termbase": self.use_termbase.isChecked(),
            "use_series_memory": self.use_memory.isChecked(),
        }