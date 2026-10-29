# ui/windows/error_window.py
from PyQt6.QtCore import Qt, QRectF, pyqtProperty
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap
from PyQt6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)
from storage.resources import IMG_ERROR, get_image_path




class ErrorWindow(QDialog):
    """Modal error dialog. The image already contains the speech bubble and
    Komi-chan; the bubble text is a label drawn on top of the image. Below it
    sits a bordered panel with the error and solution messages, then OK.
    All styling lives in the global stylesheet (see object names)."""
 
    def __init__(self, error_msg, solution_msg="", image_path=None,
                 bubble_text="WHAT DID \n YOU DO!?", window_title="Error",
                 image_width=400,
                 text_rect=(0.01, 0.2, 0.56, 0.65),
                 parent=None):
        """text_rect = (x, y, w, h) of the bubble's inside, as fractions (0-1)
        of the image size. Tune it until the text sits inside the bubble."""
        super().__init__(parent)
        self.setObjectName("errorWindow")
        self.setWindowTitle(window_title)
        self.setModal(True)
        self.setMinimumWidth(max(420, image_width + 40))
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
 
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(14)
 
        # ---- image with the bubble text overlapping it ----
        pix = QPixmap(str(image_path)) if image_path else QPixmap()
        if not pix.isNull():
            scaled = pix.scaledToWidth(
                image_width, Qt.TransformationMode.SmoothTransformation)
            image = QLabel()
            image.setObjectName("errorImage")
            image.setPixmap(scaled)
            image.setFixedSize(scaled.size())
 
            text = QLabel(bubble_text, image)          # child of the image = overlaps it
            text.setObjectName("errorBubbleText")
            text.setWordWrap(True)
            text.setAlignment(Qt.AlignmentFlag.AlignCenter)
            x, y, w, h = text_rect
            text.setGeometry(round(x * scaled.width()), round(y * scaled.height()),
                             round(w * scaled.width()), round(h * scaled.height()))
            root.addWidget(image, 0, Qt.AlignmentFlag.AlignHCenter)
        else:
            # no image: still show the line, just as a plain label
            text = QLabel(bubble_text)
            text.setObjectName("errorBubbleText")
            text.setAlignment(Qt.AlignmentFlag.AlignCenter)
            root.addWidget(text)
 
        # ---- bordered panel with both messages ----
        panel = QFrame()
        panel.setObjectName("errorPanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(14, 12, 14, 12)
        panel_layout.setSpacing(10)
 
        error_label = QLabel(error_msg)
        error_label.setObjectName("errorMessage")
        error_label.setWordWrap(True)
        error_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse)
        panel_layout.addWidget(error_label)
 
        if solution_msg:
            solution_label = QLabel(solution_msg)
            solution_label.setObjectName("errorSolution")
            solution_label.setWordWrap(True)
            solution_label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse)
            panel_layout.addWidget(solution_label)
        root.addWidget(panel)
 
        # ---- OK ----
        ok = QPushButton("OK")
        ok.setObjectName("errorOkButton")
        ok.setDefault(True)
        ok.setMinimumWidth(100)
        ok.clicked.connect(self.accept)
        root.addWidget(ok, 0, Qt.AlignmentFlag.AlignHCenter)
 
    # ------------------------------------------------------------------
    @staticmethod
    def show_error(parent, exc):
        image_path = get_image_path(IMG_ERROR)
        """Show a dialog for an exception. Works with KomiError (uses its
        user_message / solution) and with any other exception (generic text)."""
        message = getattr(exc, "user_message", None) or \
            "An unexpected error occurred. Details were saved to the log."
        solution = getattr(exc, "solution", "") or ""
        ErrorWindow(message, solution, image_path, parent=parent).exec()