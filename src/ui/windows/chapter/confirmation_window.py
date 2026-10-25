from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QVBoxLayout, QWidget,
)


class ConfirmationWindow(QDialog):
    add_correct_requested = pyqtSignal()
    add_all_requested = pyqtSignal()
    cancel_requested = pyqtSignal()

    def __init__(self, ready_count, empty_count, boxes, parent=None):
        """boxes: SegmentBox widgets of the segments with spelling errors."""
        super().__init__(parent)
        self.setObjectName("confirmationDialog")
        self.setWindowTitle("Confirm segments")
        self.setModal(True)
        self.resize(560, 640)
        self._boxes = list(boxes)

        root = QVBoxLayout(self)
        root.setSpacing(12)

        title = QLabel("Confirm segments before adding to Translation Memory")
        title.setObjectName("confirmationTitle")
        root.addWidget(title)

        # ---- summary: lines with a zero count are hidden ----
        root.addWidget(QLabel(f"{ready_count} segments are ready to be added to TM"))
        if empty_count:
            root.addWidget(QLabel(f"{empty_count} segments don't have translation"))
        if self._boxes:
            root.addWidget(QLabel(
                f"{len(self._boxes)} segments have spelling errors.\n"
                "Correct them before adding to TM."))

        # ---- scroll panel with the segment boxes ----
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.StyledPanel)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        host = QWidget()
        self.box_layout = QVBoxLayout(host)
        self.box_layout.setSpacing(10)
        for box in self._boxes:
            self.box_layout.addWidget(box)          # reparents the box into this dialog
        self.box_layout.addStretch()
        self.scroll.setWidget(host)
        self.scroll.setVisible(bool(self._boxes))
        root.addWidget(self.scroll, 1)

        # ---- buttons ----
        buttons = QHBoxLayout()
        self.add_correct_btn = QPushButton("Add only correct segments")
        self.add_all_btn = QPushButton("Include all segments with errors")
        self.cancel_btn = QPushButton("Cancel")
        self.add_correct_btn.setObjectName("primaryButton")
        self.add_all_btn.setEnabled(bool(self._boxes))   # nothing to include otherwise

        self.add_correct_btn.clicked.connect(self._on_add_correct)
        self.add_all_btn.clicked.connect(self._on_add_all)
        self.cancel_btn.clicked.connect(self.reject)
        for b in (self.add_correct_btn, self.add_all_btn, self.cancel_btn):
            buttons.addWidget(b)
        root.addLayout(buttons)

    def _on_add_correct(self):
        self.add_correct_requested.emit()
        self.accept()

    def _on_add_all(self):
        self.add_all_requested.emit()
        self.accept()

    def reject(self):                       # Cancel button, X button and Esc all end here
        self.cancel_requested.emit()
        super().reject()

    def release_boxes(self):
        """Take the boxes out of the dialog and return them, so the controller can
        put them back where they came from before the dialog is deleted."""
        for box in self._boxes:
            self.box_layout.removeWidget(box)
            box.setParent(None)
        boxes, self._boxes = self._boxes, []
        return boxes