from PyQt6.QtWidgets import QPushButton, QTextEdit
from PyQt6.QtCore import Qt, pyqtSignal


class SuggestionsTextEdit(QTextEdit):
    accepted = pyqtSignal(str)          # the suggestion the user accepted

    def __init__(self, translation_memory, parent=None):
        super().__init__(parent)
        self.translation_memory = translation_memory
        self.matches = ""
        self.best_suggestion = ""       # what [Accept] sends

        self.accept_btn = QPushButton("Accept", self.viewport())
        self.accept_btn.setObjectName("acceptSuggestion")
        self.accept_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # Important: don't take focus. Clicking would otherwise unfocus the text area,
        # which hides this widget before the click completes.
        self.accept_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.accept_btn.clicked.connect(self._on_accept)
        self.accept_btn.hide()

    def show_suggestions(self, source_text, term_matches):
        matches = ""
        term_text = ""
        tm_best = ""

        if term_matches:
            term_text = " ".join(target for _, _, _, target in term_matches)
            #matches += term_text + "\n"

        exact_matches = self.translation_memory.find_exact_matches(source_text)
        if exact_matches:
            source, target, context = exact_matches[0]
            matches += target + "\n"
            tm_best = target
        else:
            fuzzy_matches = self.translation_memory.find_fuzzy_matches(source_text)
            for source, target, context, accuracy in fuzzy_matches:
                matches += target + "\n"
                if not tm_best:                 # first fuzzy match is the best one
                    tm_best = target

        if matches:
            self.matches = matches
            # prefer a TM match; fall back to the glossary terms
            self.best_suggestion = tm_best or term_text
            self.setPlainText(matches)
            self._adjust_label_height()
            self.accept_btn.setVisible(bool(self.best_suggestion))
            self._place_button()
            self.setVisible(True)
        else:
            self.best_suggestion = ""
            self.accept_btn.hide()

    def _on_accept(self):
        if self.best_suggestion:
            self.accepted.emit(self.best_suggestion.strip())

    def _place_button(self):
        vp = self.viewport()
        b = self.accept_btn
        b.adjustSize()
        b.move(vp.width() - b.width() - 4, vp.height() - b.height() - 4)
        b.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._place_button()

    def _adjust_label_height(self):
        doc_height = int(self.document().size().height())
        self.setMaximumHeight(max(20, min(doc_height + 4, 150)))