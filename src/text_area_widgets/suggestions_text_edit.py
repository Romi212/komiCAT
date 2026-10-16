from PyQt6.QtWidgets import QMenu,  QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent,  QTextCharFormat

class SuggestionsTextEdit(QTextEdit):

    def __init__(self, translation_memory, parent=None):
        super().__init__(parent)
        self.translation_memory = translation_memory


    def show_suggestions(self, source_text, term_matches):
        matches = ""
        if(term_matches):
            
            
            for start, end, source_term, target_term in term_matches:
                matches += target_term + " "
            matches += "\n"
            
        exact_matches = self.translation_memory.find_exact_matches(source_text)
        if (exact_matches):
            source, target, context = exact_matches[0]
            matches += target + "\n"
        else:
             fuzzy_matches = self.translation_memory.find_fuzzy_matches(source_text)
             for source, target, context, acuracy in fuzzy_matches:
                  print(f"{source} > {target}, context: {context}, acuract? {acuracy}")
                  matches += target + "\n"
        if (matches):
            self.setPlainText(matches)
            self._adjust_label_height()
            self.setVisible(True)
             


    def _adjust_label_height(self):
            """Adjust label height to fit content"""
            doc_height = int(self.document().size().height())
            self.setMaximumHeight(max(20, min(doc_height + 4, 150)))
            


    
