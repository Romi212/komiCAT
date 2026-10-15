from PyQt6.QtWidgets import QApplication, QBoxLayout, QFrame, QHBoxLayout, QMenu, QSizePolicy, QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import QMimeData, Qt, pyqtSignal
from PyQt6.QtGui import QDrag, QKeyEvent, QTextCursor, QTextCharFormat, QColor
from aux_types.segment_types import SegmentType
from text_area_widgets.suggestions_text_edit import SuggestionsTextEdit
from text_area_widgets.translation_text_edit import TranslationTextEdit
from text_area_widgets.source_text_edit import SourceTextEdit

class DragHandle(QLabel):
    """Grip icon placed on the left side of SegmentBox to initiate dragging."""
    def __init__(self, parent_segment_box):
        super().__init__("⋮⋮")
        self.segment_box = parent_segment_box
        self.setFixedWidth(18)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setObjectName("DragHandle")
        self._edit_mode = False
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

    focused = pyqtSignal(object)
    deleted = pyqtSignal(object)
    # Replace with the family name of a bundled display font if you add one
    SFX_FONT_FAMILIES = '"Yu Gothic UI", "Meiryo UI", "MS Gothic", sans-serif'
    SFX_SIZE_FACTOR = 1.8

    def __init__(self, spell_checker, jp_dict, logic_segment, initial_text_size=12):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.spell_checker = spell_checker
        self.jp_dict = jp_dict
        self.on_focused = None  
        self.on_unfocused = None  
        self.segment = logic_segment
        self.text_size = initial_text_size
        self.initial_height = self.text_size * 2  
        self._edit_mode = False
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(6)

        # Drag Handle on the left
        self.drag_handle = DragHandle(self)
        main_layout.addWidget(self.drag_handle, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.drag_handle.setVisible(False)

        
        
        
        # TextEdit for Japanese text (editable)
        self.termbase = self.segment.page.chapter.get_termbase()
        self.label = SourceTextEdit(jmdict=jp_dict, termbase=self.termbase)
        self.label.set_source_text(self.segment.source_text)
        self.label.setReadOnly(False)
        self.label.setStyleSheet(f"font-weight: bold; font-size: {self.text_size}px;")
        self.label.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.label.textChanged.connect(self._adjust_label_height)

        self.label.focusInEvent = self._on_label_focus
        self.label.focusOutEvent = self._on_label_unfocus
        self.label.setTabChangesFocus(True)
        

        self.suggestions  = SuggestionsTextEdit()
        self.suggestions.setReadOnly(True)
        self.suggestions.setStyleSheet(f"font-size: {self.text_size}px;")
        self.suggestions.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.suggestions.setMinimumHeight(5)
        self.suggestions.setVisible(False)  # Initially hidden

        
        self.text_area = TranslationTextEdit(spell_checker=self.spell_checker)
        self.text_area.setPlainText(self.segment.translation)
        self.text_area.setStyleSheet(f"font-size: {self.text_size}px;")
        self.text_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.text_area.textChanged.connect(self._adjust_text_area_height)

        self.text_area.focusInEvent = self._on_text_area_focus
        self.text_area.focusOutEvent = self._on_text_area_unfocus  # Reuse unfocus for both
        self.text_area.setTabChangesFocus(True)
        
        # two dividers, only one is shown at a time
        self.h_divider = QFrame()
        self.h_divider.setObjectName("segmentDivider")
        self.h_divider.setFixedHeight(1)
        self.v_divider = QFrame()
        self.v_divider.setObjectName("segmentDivider")
        self.v_divider.setFixedWidth(1)

        for w in (self.label, self.suggestions, self.text_area, self.h_divider, self.v_divider):
            w.setParent(self)
        
        # ---------- body: one layout, direction depends on the segment type ----------
        self.body_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.body_layout.setContentsMargins(5, 5, 5, 5)
        self.body_layout.setSpacing(5)
        main_layout.addLayout(self.body_layout, 1)

        # ---------- number badge, floating in the top-right corner ----------
        self.number_badge = QLabel(self)
        self.number_badge.setObjectName("numberBadge")
        self.number_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.number_badge.setFixedSize(24, 18)

        self.setLayout(main_layout)
        self._apply_layout()
        self.refresh_number()


    def _is_sfx(self):
        return self.segment.segment_type == SegmentType.SFX

    def _apply_layout(self):
        # takeAt removes the item from the layout without deleting the widget
        while self.body_layout.count():
            self.body_layout.takeAt(0)

        if self._is_sfx():
            # [ jp text (fancy font) | translation ]
            self.body_layout.setDirection(QBoxLayout.Direction.LeftToRight)
            self.body_layout.setSpacing(10)
            self.body_layout.addWidget(self.label, 1, Qt.AlignmentFlag.AlignVCenter)
            self.body_layout.addWidget(self.v_divider)
            self.body_layout.addWidget(self.text_area, 1, Qt.AlignmentFlag.AlignVCenter)
            visible = {self.label, self.v_divider, self.text_area}
        else:
            # jp text / divider / suggestions / translation
            self.body_layout.setDirection(QBoxLayout.Direction.TopToBottom)
            self.body_layout.setSpacing(5)
            self.body_layout.addWidget(self.label)
            self.body_layout.addWidget(self.h_divider)
            self.body_layout.addWidget(self.suggestions)
            self.body_layout.addWidget(self.text_area)
            visible = {self.label, self.h_divider, self.text_area}

        # suggestions stay hidden until the text area gets focus
        for w in (self.v_divider, self.label, self.h_divider, self.suggestions, self.text_area):
            w.setVisible(w in visible)

        self._apply_label_style()
        self._adjust_height(self.label)
        self._adjust_height(self.text_area)

    def _apply_label_style(self):
        # font and size live together in the stylesheet (it overrides setFont)
        if self._is_sfx():
            size = int(self.text_size * self.SFX_SIZE_FACTOR)
            self.label.setStyleSheet(
                f"font-family: {self.SFX_FONT_FAMILIES}; font-size: {size}px; "
                "font-weight: 900; font-style: italic;")
        else:
            self.label.setStyleSheet(f"font-size: {self.text_size}px;")

    def refresh_type(self):
        """Call when the segment type changes."""
        self._apply_layout()

    def refresh_number(self):
        """Call after the segments are renumbered."""
        self.number_badge.setText(str(self.segment.nro))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.number_badge.move(self.width() - self.number_badge.width() - 6, 6)
        self.number_badge.raise_()


    def set_prev_focus(self, segment):
        if segment:
            if segment.segment_box:
                prev = segment.segment_box.text_area
                QWidget.setTabOrder(prev,self.text_area)
    def get_index(self):
        return self.segment.get_head_index()
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

    def _adjust_text_area_height(self):
        """Adjust text area height dynamically to fit text content."""
        self._adjust_height(self.text_area)

    def _adjust_label_height(self):
        """Adjust label height dynamically to fit text content."""
        self._adjust_height(self.label)
    def _adjust_height(self, widget):
        """Adjust label height dynamically to fit text content."""
        # Force document layout calculation to get accurate height
        widget.document().adjustSize()
        doc_height = int(widget.document().size().height())
        
        cap = 220 if self._is_sfx() else 150
        target_height = max(32, min(doc_height + 8, cap))
        
        # Lock minimum and maximum to force the layout engine to respect content height
        widget.setFixedHeight(target_height)
        self.updateGeometry()

    
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
        self.focused.emit(self.segment)
        if not self._is_sfx():          # the horizontal layout has no spot for suggestions
            self.suggestions.show_suggestions(self.get_japanese_text(), self.label._term_matches)
        QTextEdit.focusInEvent(self.text_area, event)


    def _on_text_area_unfocus(self, event):
        self.segment.show_focus(False)
        
        QTextEdit.focusOutEvent(self.text_area, event)
        self.segment.translation = self.get_translation()
        self.suggestions.setVisible(False)
        print(f"Updated translation for segment {self.segment.nro}: {self.segment.translation}")
        self.check_spelling() 

    def zoom(self, new_size):
        self.text_size = new_size
        print(f"New text size: {self.text_size}")
        self._apply_label_style()
        self.text_area.setStyleSheet(f"font-size: {self.text_size}px;")
        self.suggestions.setStyleSheet(f"font-size: {self.text_size}px;")
        self._adjust_label_height()
        self._adjust_text_area_height()

    def set_edit_mode(self, enabled: bool):
        self._edit_mode = enabled
        
        # Toggle drag handle visibility
        self.drag_handle.setVisible(enabled)

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
                if not self.termbase.look_up_source(word):
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
                        self.text_area.add_misspelled_word(word)
                else:
                    self.label.remove_match(word)
    def delete_self(self):
        self.drag_handle.setVisible(False)
        self.deleted.emit(self)