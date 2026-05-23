from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import Qt


class SegmentBox(QWidget):
    def __init__(self, japanese_text=""):
        super().__init__()
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Label with Japanese text
        self.label = QLabel(japanese_text)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(self.label)
        
        # Text area for translation
        self.text_area = QTextEdit()
        self.text_area.setMinimumHeight(100)
        self.text_area.setMaximumHeight(150)
        layout.addWidget(self.text_area)
        
        # Set border style
        self.setStyleSheet("""
            SegmentBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: #f9f9f9;
            }
        """)
        
        self.setLayout(layout)
        self.setMinimumHeight(150)
        self.setMaximumHeight(200)
    
    def set_japanese_text(self, text):
        self.label.setText(text)
    
    def get_translation(self):
        return self.text_area.toPlainText().strip()
    
    def set_translation(self, text):
        self.text_area.setPlainText(text)