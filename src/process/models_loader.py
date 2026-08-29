from PyQt6.QtCore import QRunnable, QObject, pyqtSignal

class ModelLoaderSignals(QObject):
    # Signal emitted when model loading is complete
    finished = pyqtSignal(object)  # Passes loaded model instance (or dict of models)
    error = pyqtSignal(str)       # Passes error message if loading fails

class ModelLoaderWorker(QRunnable):
    def __init__(self, load_function, *args, **kwargs):
        super().__init__()
        self.load_function = load_function
        self.args = args
        self.kwargs = kwargs
        self.signals = ModelLoaderSignals()

    def run(self):
        try:
            # Executes the blocking loading call in the background thread
            result = self.load_function(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))