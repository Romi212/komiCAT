from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QLabel, QFileDialog, QScrollArea, QGraphicsScene, QGraphicsView,
    QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsProxyWidget
)
from PyQt6.QtGui import QPixmap, QImage, QColor, QPen, QIcon
from PyQt6.QtCore import Qt, QSize, QRect
from PIL import Image
import os

from text_extractor import TextExtractor
from aux_types.text_box import TextBox
from aux_types.text_box_button import TextBoxButton
from views_adapter import ViewsAdapter


class ImageViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text_extractor = TextExtractor()
        self.detected_bubbles = []
        self.detected_text_areas_buttons = []
        self.detected_text_bubbles = []
        self.detected_free_text = []
        self.selected_bubbles = []
        self.current_image = 0
        self.loaded_images = []  
        
        # Current image and zoom
        self.original_image = None
        self.current_pixmap = None
        self.zoom_factor = 1.0
        
        # Setup UI
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        image_nav_layout = QHBoxLayout()
        self.prev_image_button = QPushButton("<")
        self.prev_image_button.clicked.connect(self.load_previous_image)
        image_nav_layout.addWidget(self.prev_image_button)

        self.image_index_label = QLabel("No image loaded")
        image_nav_layout.addWidget(self.image_index_label)

        self.next_image_button = QPushButton(">")
        self.next_image_button.clicked.connect(self.load_next_image)
        image_nav_layout.addWidget(self.next_image_button)

        layout.addLayout(image_nav_layout)


        # Graphics view for image display with zoom
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view.wheelEvent = self.on_mouse_wheel
        layout.addWidget(self.view)
        
        # Status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        # Button bar
        button_layout = QHBoxLayout()
        
        self.open_button = QPushButton("Open Image")
        self.open_button.clicked.connect(self.load_image)
        button_layout.addWidget(self.open_button)
        
        self.reset_zoom_button = QPushButton("Reset Zoom")
        self.reset_zoom_button.clicked.connect(self.reset_zoom)
        button_layout.addWidget(self.reset_zoom_button)
        
        self.detect_bubbles_button = QPushButton("Detect Bubbles")
        self.detect_bubbles_button.clicked.connect(self.detect_bubbles)
        button_layout.addWidget(self.detect_bubbles_button)
        
        self.extract_text_button = QPushButton("Extract Text")
        self.extract_text_button.clicked.connect(self.extract_text)
        button_layout.addWidget(self.extract_text_button)

        self.clear_selection_button = QPushButton("Clear Selection")
        self.clear_selection_button.clicked.connect(self.clear_selection)
        button_layout.addWidget(self.clear_selection_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.setWindowTitle("Image Viewer")
        self.resize(1000, 800)
        
    def set_adapter(self, adapter):
        self.adapter = adapter
        
    def load_image(self):
        self.file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Open Image File",
            "",
            "Image files (*.png *.jpg *.jpeg *.gif *.bmp *.ico);;All files (*)"
        )
        for file_path in self.file_paths:
            try:
                image = Image.open(file_path)
                self.loaded_images.append(image)
                self.status_label.setText(f"Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                self.status_label.setText(f"Error opening file: {str(e)}")
                print(f"Error: {e}")
        self.zoom_factor = 1.0
        self.image_index_label.setText(self.file_paths[0] if self.file_paths else "No image loaded")
        self.original_image = self.loaded_images[0] if self.loaded_images else None
        self._setup_image()
    
    def _setup_image(self):
        """Set up the image in the scene (called once when loading)"""
        if self.original_image:
            try:
                
                pil_image = self.original_image.convert("RGB")
                data = pil_image.tobytes("raw", "RGB")
                bytes_per_line = 3 * pil_image.width
                q_image = QImage(data, pil_image.width, pil_image.height, bytes_per_line, QImage.Format.Format_RGB888)
                self.current_pixmap = QPixmap.fromImage(q_image)
                
                # Clear scene and add pixmap
                self.scene.clear()
                self.scene.addPixmap(self.current_pixmap)
                #self.view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
            except Exception as e:
                self.status_label.setText(f"Error setting up image: {str(e)}")
                print(f"Error: {e}")
            
    def update_image(self):
        """Update the view zoom level using transform"""
        if self.original_image:
            try:
                # Reset and apply zoom transform to the view
                self.view.resetTransform()
                self.view.scale(self.zoom_factor, self.zoom_factor)
                self.status_label.setText(f"Zoom: {self.zoom_factor:.2f}x")
            except Exception as e:
                self.status_label.setText(f"Error updating zoom: {str(e)}")
                print(f"Error: {e}")
            
    def zoom_in(self):
        self.zoom_factor *= 1.2
        self.update_image()
        
        
    def zoom_out(self):
        self.zoom_factor /= 1.2
        self.update_image()
        
        
    def reset_zoom(self):
        self.zoom_factor = 1.0
        self.update_image()
        
        
    def on_mouse_wheel(self, event):
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()
            
    def selected_bubble(self, bubble_button):
        print(f"Selected bubble")
        if bubble_button not in self.selected_bubbles and not bubble_button.has_been_extracted_flag:
            self.selected_bubbles.append(bubble_button)
            bubble_button.selected(len(self.selected_bubbles))
            
    def detect_bubbles(self):
        if self.current_pixmap:
            # Always detect from original image (no zoom-based resizing)
            self.detected_bubbles, self.detected_text_bubbles, self.detected_free_text = \
                self.text_extractor.detect_speech_bubbles(self.original_image)
            
            for bubble in self.detected_text_bubbles + self.detected_free_text:
                # Create button based on original image coordinates
                button = TextBoxButton(
                    bubble,
                    width=bubble.xmax - bubble.xmin,
                    height=bubble.ymax - bubble.ymin,
                    alpha=0.6
                )

                button.link_on_click(lambda checked, btn=button: self.selected_bubble(btn))
                self.detected_text_areas_buttons.append(button)
                
                # Add to scene at original coordinates (zoom transform will scale it)
                proxy = self.scene.addWidget(button)
                proxy.setPos((bubble.xmin + bubble.xmax) // 2 - button.width() // 2, bubble.ymin)
                
                
    def extract_text(self):
        if (self.detected_text_bubbles or self.detected_free_text) and self.current_pixmap:
            if len(self.selected_bubbles) == 0:
                print("No bubbles selected, extracting text from all detected bubbles")
            else:
                self.text_extractor.extract_text(
                    self.original_image,
                    [button.text_box for button in self.selected_bubbles]
                )
                self.adapter.AddSegments(self.selected_bubbles)
                self.selected_bubbles = []  # Clear selection after extraction

    def clear_selection(self):
        for button in self.selected_bubbles:
            button.uncheck()
        self.selected_bubbles = []
           
    def load_previous_image(self):
        if self.current_image >0:
             self.current_image -= 1
             self.original_image = self.loaded_images[self.current_image]
             self.image_index_label.setText(os.path.basename(self.file_paths[self.current_image] if self.file_paths else "No image loaded"))
             self._setup_image()
        

    def load_next_image(self):
        if self.current_image < len(self.loaded_images) - 1:
             self.current_image += 1
             self.image_index_label.setText(os.path.basename(self.file_paths[self.current_image] if self.file_paths else "No image loaded"))
             self.original_image = self.loaded_images[self.current_image]
             self._setup_image()
        