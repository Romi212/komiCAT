from PyQt6.QtWidgets import QApplication, QHBoxLayout, QMenu, QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import QMimeData, Qt
from PyQt6.QtGui import QDrag, QKeyEvent, QTextCursor, QTextCharFormat, QColor
from text_area_widgets.translation_text_edit import TranslationTextEdit

class DragHandle(QLabel):
    """Grip icon placed on the left side of SegmentBox to initiate dragging."""
    def __init__(self, parent_segment_box):
        super().__init__("⋮⋮")
        self.segment_box = parent_segment_box
        self.setFixedWidth(18)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 16px;
                font-weight: bold;
                background-color: #e2e2e2;
                border-radius: 3px;
            }
            QLabel:hover {
                background-color: #cccccc;
                color: #222222;
            }
        """)
        self._drag_start_pos = None
        self.callback = None  # Placeholder for the callback function

    def set_drag_callback(self, callback):
        """Set the callback function to be called when dragging starts."""
        self.callback = callback

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        drag = QDrag(self)
        
        # Qt requires a QMimeData object to initiate a QDrag, 
        # but you can leave it empty or attach a direct reference.
        mime_data = QMimeData()
        drag.setMimeData(mime_data)

        # Store a direct Python pointer to the widget on the class or container
        self.callback(self.segment_box)  # Call the callback to set the active drag widget

        # Optional ghost preview
        pixmap = self.segment_box.grab()
        drag.setPixmap(pixmap.scaledToWidth(250, Qt.TransformationMode.SmoothTransformation))

        drag.exec(Qt.DropAction.MoveAction)
        self.callback(None)  # Clear the active drag widget after the drag operation

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.CursorShape.OpenHandCursor)

class SegmentBox(QWidget):


    def __init__(self, spell_checker, logic_segment, initial_text_size=12):
        super().__init__()
        self.spell_checker = spell_checker
        self.on_focused = None  
        self.on_unfocused = None  
        self.segment = logic_segment
        self.text_size = initial_text_size
        self.initial_height = self.text_size * 2  

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(6)

        # Drag Handle on the left
        self.drag_handle = DragHandle(self)
        main_layout.addWidget(self.drag_handle, alignment=Qt.AlignmentFlag.AlignVCenter)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        
        # TextEdit for Japanese text (editable)
        self.label = TranslationTextEdit(spell_checker=self.spell_checker)
        self.label.setPlainText(self.segment.source_text)
        self.label.setReadOnly(False)
        self.label.setMinimumHeight(5)
        self.label.setStyleSheet(f"font-weight: bold; font-size: {self.text_size}px;")
        self.label.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.label.textChanged.connect(self._adjust_label_height)
        self.label.focusInEvent = self._on_label_focus
        self.label.focusOutEvent = self._on_label_unfocus
        layout.addWidget(self.label)
        
        # Text area for translation
        self.text_area = TranslationTextEdit(spell_checker=self.spell_checker)
        self.text_area.setMinimumHeight(5)
        self.text_area.setMaximumHeight(self.initial_height)
        self.text_area.setPlainText(self.segment.translation)
        self.text_area.setStyleSheet(f"font-size: {self.text_size}px;")
        self.text_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.text_area.textChanged.connect(self._adjust_text_area_height)
        self.text_area.focusInEvent = self._on_text_area_focus
        self.text_area.focusOutEvent = self._on_text_area_unfocus  # Reuse unfocus for both
        layout.addWidget(self.text_area)

        main_layout.addLayout(layout)
        # Set border style
        self.setStyleSheet("""
            SegmentBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: #f9f9f9;
                
                           
            }
        """)
        
        self.setLayout(main_layout)
        self.setMinimumHeight(5)
        
        # Adjust initial heights
        self._adjust_label_height()
    def set_drag_callback(self, callback):
        """Set the callback function to be called when dragging starts."""
        self.drag_handle.set_drag_callback(callback)
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
        self.segment.show_focus(True)
        QTextEdit.focusInEvent(self.label, event)


    def _on_label_unfocus(self, event):
        self.segment.show_focus(False)
        self.segment.source_text = self.get_japanese_text()
        print(f"Updated source text for segment {self.segment.nro}: {self.segment.source_text}")
        QTextEdit.focusOutEvent(self.label, event)
        

    def _on_text_area_focus(self, event):
        self.segment.show_focus(True)
        QTextEdit.focusInEvent(self.text_area, event)


    def _on_text_area_unfocus(self, event):
        self.segment.show_focus(False)
        
        QTextEdit.focusOutEvent(self.text_area, event)
        self.segment.translation = self.get_translation()
        print(f"Updated translation for segment {self.segment.nro}: {self.segment.translation}")
        self.check_spelling() 

    def zoom(self, new_size):
        self.text_size = new_size
        print(f"New text size: {self.text_size}")
        self.label.setStyleSheet(f"font-weight: bold; font-size: {self.text_size}px;")
        self.text_area.setStyleSheet(f"font-size: {self.text_size}px;")
        self._adjust_label_height()
        self._adjust_text_area_height()

    def check_spelling(self):
        if not self.get_translation().strip():  # Only check if there's text
            return
        """Check spelling of the translation text and highlight misspelled words."""
        text = self.get_translation()
        misspelled_words = self.spell_checker.get_misspelled_words(text)

        if misspelled_words:
            print(f"Misspelled words in segment {self.segment.nro}: {misspelled_words}")
 
            # Configure the underline format
            fmt = QTextCharFormat()
            fmt.setFontUnderline(True) 
            # Optional: Custom underline styling (like a red wavy spellcheck line)
            #fmt.setUnderlineStyle(QTextCharFormat.WaveUnderline)
            fmt.setUnderlineColor(QColor("red"))

            # Obtain document cursor
            doc = self.text_area.document()

            for word in misspelled_words:
                # Clear previous cursor adjustments and search from beginning
                cursor = QTextCursor(doc)
                while True:
                    # Find the next occurrence of the word
                    cursor = doc.find(word, cursor)
                    
                    # If no more matches are found, break loop
                    if cursor.isNull():
                        break
                        
                    # Apply formatting specifically to the matched cursor selection
                    cursor.mergeCharFormat(fmt)

            