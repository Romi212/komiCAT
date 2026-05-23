import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QSplitter, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

from image_viewer import ImageViewer
from text_viewer import TextViewer
from views_adapter import ViewsAdapter


def main():
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("Text and Image Viewer")
    window.resize(1600, 900)
    
    # Create central widget with splitter
    central_widget = QWidget()
    layout = QVBoxLayout()
    
    splitter = QSplitter(Qt.Orientation.Horizontal)
    
    # Create viewers
    text_viewer = TextViewer()
    image_viewer = ImageViewer()
    
    # Add to splitter
    splitter.addWidget(text_viewer)
    splitter.addWidget(image_viewer)
    splitter.setStretchFactor(0, 1)
    splitter.setStretchFactor(1, 2)
    
    layout.addWidget(splitter)
    central_widget.setLayout(layout)
    window.setCentralWidget(central_widget)
    
    # Setup adapter
    views_adapter = ViewsAdapter(image_viewer, text_viewer)
    image_viewer.set_adapter(views_adapter)
    
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()