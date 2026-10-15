from PyQt6.QtWidgets import QMenu,  QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent,  QTextCharFormat

class SuggestionsTextEdit(QTextEdit):

    def __init__(self, parent=None):
        super().__init__(parent)


    def show_suggestions(self, source_text, term_matches):
        if(term_matches):
            
            matches = ""
            for start, end, source_term, target_term in term_matches:
                matches += target_term + " "

            self.setPlainText(matches)
            self._adjust_label_height()
            self.setVisible(True)


    def _adjust_label_height(self):
            """Adjust label height to fit content"""
            doc_height = int(self.document().size().height())
            self.setMaximumHeight(max(20, min(doc_height + 4, 150)))
            


    
