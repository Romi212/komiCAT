from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import Qt


class SegmentBox(QWidget):
    def __init__(self, japanese_text=""):
        super().__init__()
        self.on_focused = None  # Callback for when this segment gets focus
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        self.text_size = 12
        
        # TextEdit for Japanese text (editable)
        self.label = QTextEdit()
        self.label.setPlainText(japanese_text)
        self.label.setReadOnly(False)
        self.label.setMinimumHeight(25)
        self.label.setStyleSheet("font-weight: bold; font-size: 12px;")
        self.label.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.label.textChanged.connect(self._adjust_label_height)
        self.label.focusInEvent = self._on_label_focus
        self.label.focusOutEvent = self._on_label_unfocus
        layout.addWidget(self.label)
        
        # Text area for translation
        self.text_area = QTextEdit()
        self.text_area.setMinimumHeight(25)
        self.text_area.setStyleSheet("font-size: 12px;")
        self.text_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.text_area.textChanged.connect(self._adjust_text_area_height)
        self.text_area.focusInEvent = self._on_label_focus
        self.text_area.focusOutEvent = self._on_label_unfocus  # Reuse unfocus for both
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
        self.setMinimumHeight(40)
        
        # Adjust initial heights
        self._adjust_label_height()
    
    def set_japanese_text(self, text):
        self.label.setPlainText(text)
        self._adjust_label_height()
    
    def get_japanese_text(self):
        return self.label.toPlainText().strip()
    
    def get_translation(self):
        return self.text_area.toPlainText().strip()
    
    def set_translation(self, text):
        self.text_area.setPlainText(text)
        self._adjust_text_area_height()
    
    def _adjust_label_height(self):
        """Adjust label height to fit content"""
        doc_height = int(self.label.document().size().height())
        self.label.setMaximumHeight(max(20, min(doc_height + 4, 150)))
    
    def _adjust_text_area_height(self):
        """Adjust text_area height to fit content"""
        doc_height = int(self.text_area.document().size().height())
        self.text_area.setMaximumHeight(max(20, min(doc_height + 4, 200)))
    
    def _on_label_focus(self, event):
        """Called when label gets focus"""
        if self.on_focused:
            self.on_focused(self)
        # Call the original focusInEvent
        QTextEdit.focusInEvent(self.label, event)


    def _on_label_unfocus(self, event):
        """Called when label loses focus"""
        if self.on_unfocused:
            self.on_unfocused(self)
        QTextEdit.focusOutEvent(self.label, event)

    def zoom(self, factor):
        """Zoom in/out by adjusting font size"""
        print(f"Zooming segment {self.text_size}")
        self.text_size = max(6, min(48, int(self.text_size * factor)))
        print(f"New text size: {self.text_size}")
        self.label.setStyleSheet(f"font-weight: bold; font-size: {self.text_size}px;")
        self.text_area.setStyleSheet(f"font-size: {self.text_size}px;")