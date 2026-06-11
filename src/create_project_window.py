import sys
from PyQt6.QtWidgets import QComboBox, QDialog, QDialogButtonBox, QFileDialog, QFormLayout, QVBoxLayout, QHBoxLayout, QSpinBox, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt

class CreateProjectWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Create New Project")
        self.resize(400, 200)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        # Project name input
       # Main layout
        main_layout = QVBoxLayout(self)
        
        # Form layout for nice aligned inputs
        form_layout = QFormLayout()
        
        # 1. Project Name Input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("My Manga Project")
        form_layout.addRow("Project Name:", self.name_input)
        
        # 2. File Path Input (with a Browse button)
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True) # Force them to use the browser
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_folder)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_btn)
        form_layout.addRow("Project Folder:", path_layout)
        
        # 3. Source Language Selection
        self.lang_input = QComboBox()
        self.lang_input.addItems(["Japanese"])
        form_layout.addRow("Source Language:", self.lang_input)
        self.output_lang_input = QComboBox()
        self.output_lang_input.addItems(["Spanish"])
        form_layout.addRow("Output Language:", self.output_lang_input)

        self.series_name_input = QLineEdit()
        self.series_name_input.setPlaceholderText("Manga Title")
        form_layout.addRow("Series Title:", self.series_name_input)


        # Replace QLineEdit with QIntSpinBox
        self.number_input = QSpinBox()
        self.number_input.setValue(1)  # Default value
        self.number_input.setMinimum(1)  # Minimum chapter number
        self.number_input.setMaximum(9999)  # Maximum chapter number
        form_layout.addRow("Chapter number:", self.number_input)

        # In get_project_data(), change to:
        
        
        main_layout.addLayout(form_layout)
        
        # 4. Standard OK / Cancel Buttons
        # QDialogButtonBox handles standard OS placement (OK on left or right depending on Windows/Mac/Linux)
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept) # Built-in QDialog method
        self.button_box.rejected.connect(self.reject) # Built-in QDialog method
        main_layout.addWidget(self.button_box)

    def _browse_folder(self):
        """Opens a native directory selector dialog"""
        folder = QFileDialog.getExistingDirectory(self, "Select Manga Source Folder")
        if folder:
            self.path_input.setText(folder)

    def get_project_data(self):
        """Helper method to grab the clean data once the user hits OK"""
        return {
            "name": self.name_input.text().strip(),
            "path": self.path_input.text(),
            "series_name": self.series_name_input.text().strip(),
            "number": self.number_input.value(),
            "source_language": self.lang_input.currentText(),
            "output_language": self.output_lang_input.currentText()
        }