from PyQt6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFileDialog, QFormLayout,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize, Qt


class CreateChapterWindow(QDialog):
    COVER_SIZE = (150, 210)   # width, height (roughly manga cover proportions)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add a new Chapter")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.cover_path = ""

        main_layout = QHBoxLayout(self)          
        main_layout.setSpacing(16)

        
        left_layout = QVBoxLayout()

        form = QFormLayout()

        self.series_name_input = QLineEdit()
        self.series_name_input.setPlaceholderText("Chapter title")
        form.addRow("Series name:", self.series_name_input)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("My Manga Project")
        form.addRow("Project name:", self.name_input)

        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_folder)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        form.addRow("Project folder:", path_layout)

        lang_layout = QHBoxLayout()
        self.lang_input = QComboBox()
        self.lang_input.addItems(["jp"])
        self.output_lang_input = QComboBox()
        self.output_lang_input.addItems(["es", "en"])
        lang_layout.addWidget(self.lang_input)
        lang_layout.addWidget(QLabel(">"))
        lang_layout.addWidget(self.output_lang_input)
        lang_layout.addStretch()
        form.addRow("Source lan:", lang_layout)

        left_layout.addLayout(form)

        left_layout.addStretch()                 # pushes the buttons to the bottom

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.setCenterButtons(True) 
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        left_layout.addWidget(self.button_box)

        main_layout.addLayout(left_layout, 1)

        # cover column
        self.cover_btn = QPushButton("Click to\nadd cover")
        self.cover_btn.setObjectName("coverButton")     # styled in build_qss
        self.cover_btn.setFixedSize(*self.COVER_SIZE)
        self.cover_btn.setIconSize(QSize(*self.COVER_SIZE))
        self.cover_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cover_btn.setToolTip("Click to choose a cover image")
        self.cover_btn.clicked.connect(self._choose_cover)
        main_layout.addWidget(self.cover_btn, alignment=Qt.AlignmentFlag.AlignTop)



       

        # OK stays disabled until the required fields are filled in
        for field in (self.series_name_input, self.name_input, self.path_input):
            field.textChanged.connect(self._validate)
        self._validate()

    # ---------- behavior ----------
    def _validate(self):
        ok = bool(self.series_name_input.text().strip()
                  and self.name_input.text().strip()
                  and self.path_input.text().strip())
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(ok)

    def _browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select where to create the project")
        if folder:
            self.path_input.setText(folder)

    def _choose_cover(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select cover image", "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp)")
        if not path:
            return
        pix = QPixmap(path)
        if pix.isNull():
            return                                      # not a readable image
        self.cover_path = path
        scaled = pix.scaled(self.cover_btn.size(),
                            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                            Qt.TransformationMode.SmoothTransformation)
        # crop to the button size so the cover fills it without stretching
        x = (scaled.width() - self.cover_btn.width()) // 2
        y = (scaled.height() - self.cover_btn.height()) // 2
        cropped = scaled.copy(x, y, self.cover_btn.width(), self.cover_btn.height())
        self.cover_btn.setText("")
        self.cover_btn.setIcon(QIcon(cropped))

    def get_project_data(self):
        return {
            "chapter_name": self.series_name_input.text().strip()
        }