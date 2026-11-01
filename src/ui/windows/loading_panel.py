# ui/windows/loading_panel.py
from PyQt6.QtCore import Qt, QEvent, QThreadPool
from PyQt6.QtGui import QImage, QImageReader, QMovie
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget
from storage.resources import get_image_path, IMG_LOAD

class LoadingPanel(QFrame):
    """Reusable panel: animated GIF + message. Put it in any layout or window.
    The animation runs only while the panel is visible."""

    def __init__(self, message="Loading...", gif_height=96, parent=None):
        super().__init__(parent)
        gif_path = get_image_path(IMG_LOAD)
        self.setObjectName("loadingPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(10)

        self.image_label = QLabel()
        self.image_label.setObjectName("loadingImage")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label, 0, Qt.AlignmentFlag.AlignHCenter)

        self.movie = QMovie(str(gif_path))
        if self.movie.isValid():
            # read the original size WITHOUT touching the movie
            size = QImageReader(str(gif_path)).size()
            if not size.isValid() or size.isEmpty():
                size = QImage(str(gif_path)).size()          # fallback: loads first frame only

            if not size.isEmpty():
                size.scale(10_000, gif_height, Qt.AspectRatioMode.KeepAspectRatio)
                self.movie.setScaledSize(size)               # before any frame is decoded
                self.image_label.setFixedSize(size)          # stops the layout from jumping

            self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
            self.image_label.setMovie(self.movie)
        else:
            self.image_label.hide()                    # no gif: text only

        self.text_label = QLabel(message)
        self.text_label.setObjectName("loadingText")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setWordWrap(True)
        layout.addWidget(self.text_label)

    def set_message(self, text):
        self.text_label.setText(text)

    # animation follows visibility, so show()/hide() is all you need
    def showEvent(self, event):
        super().showEvent(event)
        if self.movie.isValid():
            self.movie.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.movie.stop()


class LoadingOverlay(QWidget):
    """Dims a whole window/widget and shows a LoadingPanel in the center.
    Follows the parent's size. Usage:
        self.loading = LoadingOverlay(self, gif_path)
        self.loading.show_loading("Detecting bubbles...")
        ...
        self.loading.hide_loading()
    """

    def __init__(self, parent,  message="Loading...", gif_height=96):
        super().__init__(parent)
        self.setObjectName("loadingOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)  # lets QSS paint the dim

        layout = QVBoxLayout(self)
        self.panel = LoadingPanel( message, gif_height)
        layout.addWidget(self.panel, 0, Qt.AlignmentFlag.AlignCenter)

        parent.installEventFilter(self)       # follow parent resizes
        self.hide()

    def show_loading(self, message=None):
        if message:
            self.panel.set_message(message)
        self.setGeometry(self.parentWidget().rect())
        self.raise_()
        self.show()

    def hide_loading(self):
        self.hide()

    def eventFilter(self, obj, event):
        if obj is self.parentWidget() and event.type() == QEvent.Type.Resize and self.isVisible():
            self.setGeometry(self.parentWidget().rect())
        return super().eventFilter(obj, event)


def run_with_loading(overlay, message, func, on_done, on_error):
    """Run func in a background thread while the overlay is shown.
    on_done(result) and on_error(err) run in the GUI thread, after the overlay is hidden."""
    from storage.process.background_worker import BackgroundWorker   # your existing class

    overlay.show_loading(message)
    worker = BackgroundWorker(func)

    def done(result):
        try:
            on_done(result)
        finally:
            overlay.hide_loading()

    def failed(err):
        try:
            on_error(err)
        finally:
            overlay.hide_loading()

    worker.signals.finished.connect(done)
    worker.signals.error.connect(failed)
    QThreadPool.globalInstance().start(worker)