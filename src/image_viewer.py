from PyQt6.QtWidgets import (
    QGraphicsSimpleTextItem, QMainWindow, QMessageBox, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QLabel, QFileDialog, QScrollArea, QGraphicsScene, QGraphicsView,
    QGraphicsPixmapItem, QGraphicsRectItem
)
from PyQt6.QtGui import QFont, QPixmap, QImage, QColor, QPen, QIcon
from PyQt6.QtCore import QRectF, Qt, QSize, QRect
from PIL import Image
import os

from image_area_widgets.text_box_rect import TextBoxRect
from tools.text_extractor import TextExtractor
from data_structure.text_box import TextBox
from data_structure.page import Page
from data_structure.segment import Segment

class ImageViewer(QWidget):
    def __init__(self, controller, parent=None, chapter=None, text_extractor=None):
        super().__init__(parent)
        self.text_extractor = text_extractor 
        self.controller = controller
        self.chapter = chapter
        self.current_page = None
        self.can_edit = False
        self.selected_bubbles = []
        self.edit_menu = None
        
        self.zoom_factor = 1.0
        
        # Setup UI
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        image_nav_layout = QHBoxLayout()
        self.prev_image_button = QPushButton("<") #TODO change to a left arrow icon
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

        self.edit_menu = QWidget(self.view)
        self.edit_menu.setObjectName("editMenu")
        self.edit_menu.setVisible(False)
        self.edit_menu.setStyleSheet(
            """
            QWidget#editMenu {
                background: rgba(25, 25, 25, 180);
                border: 1px solid rgba(255, 255, 255, 120);
                border-radius: 8px;
            }
            QWidget#editMenu QPushButton {
                min-width: 110px;
                padding: 8px 10px;
                border-radius: 6px;
            }
            """
        )
        edit_menu_layout = QVBoxLayout(self.edit_menu)
        edit_menu_layout.setContentsMargins(8, 8, 8, 8)
        edit_menu_layout.setSpacing(6)

        self.add_segment_button = QPushButton("Add Segment")
        self.add_segment_button.clicked.connect(self.add_segment)
        edit_menu_layout.addWidget(self.add_segment_button)

        self.reorder_button = QPushButton("Reorder")
        self.reorder_button.clicked.connect(self.reorder_segments)
        edit_menu_layout.addWidget(self.reorder_button)

        self._update_edit_menu_position()
        
        # Status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        # TODO change text to include translations
        self.button_layout = QHBoxLayout()
        
        self.open_button = QPushButton("Open Images")
        self.open_button.clicked.connect(self.open_images)
        #self.button_layout.addWidget(self.open_button)

        self.detect_bubbles_button = QPushButton("Batch detect Bubbles")
        self.detect_bubbles_button.clicked.connect(self.detect_all_pages)
        self.button_layout.addWidget(self.detect_bubbles_button)
        
        self.detect_page_bubbles_button = QPushButton("Detect page Bubbles")
        self.detect_page_bubbles_button.clicked.connect(self.detect_page_bubbles)
        self.button_layout.addWidget(self.detect_page_bubbles_button)

        self.batch_extract_text_button = QPushButton("Extract all text")
        self.batch_extract_text_button.clicked.connect(self.batch_extract_text)
        self.button_layout.addWidget(self.batch_extract_text_button)
        
        
        self.extract_text_button = QPushButton("Extract Text")
        self.extract_text_button.clicked.connect(self.extract_text)
        self.button_layout.addWidget(self.extract_text_button)

        self.edition_mode_button = QPushButton("Edition Mode")
        self.edition_mode_button.setCheckable(True)  # Enables checkable/toggle state
        self.edition_mode_button.toggled.connect(self.edit_mode)  # Sends boolean (True/False)
        self.button_layout.addWidget(self.edition_mode_button)

        self.clear_selection_button = QPushButton("Clear Selection")
        self.clear_selection_button.clicked.connect(self.clear_selection)
        #button_layout.addWidget(self.clear_selection_button)

        self.add_bubble_button = QPushButton("Add Bubble")
        self.add_bubble_button.clicked.connect(self.add_bubble)
        #button_layout.addWidget(self.add_bubble_button)
        
        layout.addLayout(self.button_layout)
        self.setLayout(layout)
        self.setWindowTitle("Image Viewer")
        self.resize(1000, 800)
        
        
    def open_images(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Open Image File",
            "",
            "Image files (*.png *.jpg *.jpeg *.gif *.bmp *.ico);;All files (*)"
        )
        if file_paths:
            self.load_pages(file_paths)
        
    def load_chapter(self, chapter):
        self.chapter = chapter
        #self.load_pages([page.file_path for page in chapter.pages])
        if len(chapter.pages) > 0:
            self.current_page = chapter.get_current_page()
            self._setup_page()
    
    def load_pages(self, file_paths):
        for file_path in file_paths:
            try:
                image = Image.open(file_path)
                page = Page(file_path=file_path, image=image, chapter=self.chapter, number=len(self.chapter.pages))
                self.chapter.add_page(page)
                self.status_label.setText(f"Loaded: {page.page_name}")
            except Exception as e:
                self.status_label.setText(f"Error opening file: {str(e)}")
                print(f"Error: {e}")
        self.zoom_factor = 1.0
        if file_paths:
            self._setup_page()

    def _setup_page(self):
        self.current_page = self.chapter.get_current_page()

        #Set up image
        
        if self.current_page:
            try:
                current_image = self.current_page.image
                pil_image = current_image.convert("RGB")
                data = pil_image.tobytes("raw", "RGB")
                bytes_per_line = 3 * pil_image.width
                q_image = QImage(data, pil_image.width, pil_image.height, bytes_per_line, QImage.Format.Format_RGB888)
                current_pixmap = QPixmap.fromImage(q_image)
                
                # Clear scene and add pixmap
                for item in self.scene.items():
                    self.scene.removeItem(item)
                self.selected_bubbles = []
                self.detect_page_bubbles_button.setDisabled(self.current_page.has_been_processed)
                self.scene.addPixmap(current_pixmap)
                self.image_index_label.setText(self.current_page.page_name)
                self.status_label.setText(f"Image loaded: {self.current_page.page_name}")
            except Exception as e:
                self.status_label.setText(f"Error setting up image: {str(e)}")
                print(f"Error: {e}")

        #Add bubble butons if it had been detected before
        
        
            for segment in self.current_page.segments:
                
                if(segment.button):
                    button = segment.button
                else:
                    button = TextBoxRect(segment.text_box, alpha=0.6)
                    segment.button = button
                    button.set_segment(segment)

                
                button.link_on_click(lambda checked, btn=segment.button: self.selected_bubble(btn))
                button.conect_signals(self.prompt_and_delete_segment, self.combine_segments)
                
                self.scene.addItem(button)
                    
            i = 0
            for panel in self.current_page.detected_panels:
                print(f"Panel {i}")
                #Create a square to show panel but not button
                x = panel.text_box.xmin
                y = panel.text_box.ymin
                w = panel.text_box.xmax - panel.text_box.xmin
                h = panel.text_box.ymax - panel.text_box.ymin

                panel_rect = QGraphicsRectItem( x,y,w,h )
                panel_rect.setPen(QPen(QColor(255, 0, 0), 2))
                self.scene.addItem(panel_rect)
                panel_text = QGraphicsSimpleTextItem(f"Panel {i + 1}")
                panel_text.setPos(x + 5, y + 5)
                panel_text.setBrush(QColor(255, 0, 0))
                panel_text.setFont(QFont("Arial", 24, QFont.Weight.Bold))
                self.scene.addItem(panel_text)
                i += 1

            
            
    def resize_page(self):
        """Update the view zoom level using transform"""
        if self.current_page:
            try:
                self.view.resetTransform()
                self.view.scale(self.zoom_factor, self.zoom_factor)
                self.status_label.setText(f"Zoom: {self.zoom_factor:.2f}x")
            except Exception as e:
                self.status_label.setText(f"Error updating zoom: {str(e)}")
                print(f"Error: {e}")
            
    def zoom_in(self):
        self.zoom_factor *= 1.2
        self.resize_page()
        
        
    def zoom_out(self):
        if(self.zoom_factor > 0.1):  # Prevent zooming out too much
            self.zoom_factor /= 1.2
            self.resize_page()
        
        
    def reset_zoom(self):
        self.zoom_factor = 1.0
        self.resize_page()
        
        
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
        
        if self.current_page and not self.current_page.has_been_processed:
            current_image = self.current_page.image
            
            detected_panels = self.text_extractor.detect_panels(current_image)
            
            detected_bubbles, detected_text_bubbles, detected_free_text = \
                            self.text_extractor.detect_speech_bubbles(current_image)

            #Stores everything in current page and sorts them
            self.current_page.store_detected_bubbles(detected_bubbles, detected_text_bubbles, detected_free_text, detected_panels)

    def extract_text(self):
        if self._finish_editing_mode():
            segments = self.current_page.get_segments_to_extract(all_segments = True)
            for segment in segments:
                text_box = segment.text_box
                self.text_extractor.extract_text(self.current_page.image,[text_box])
                segment.has_been_extracted()

            self.controller.extracted(self.current_page, segments)


            """else:
                #Updates actual coordinates if button was moved by user
                for button in self.selected_bubbles:

                    scene_rect = button.mapToScene(button.rect()).boundingRect()

                    button.text_box.xmin = scene_rect.left()
                    button.text_box.ymin = scene_rect.top()
                    button.text_box.xmax = scene_rect.right()
                    button.text_box.ymax = scene_rect.bottom()

                #Extracts texts and stores it directly in text_boxes        
                self.text_extractor.extract_text(
                    self.current_page.image,
                    [button.text_box for button in self.selected_bubbles]
                )
                self.controller.extracted(self.current_page,self.selected_bubbles)
                self.selected_bubbles = []  # Clear selection after extraction"""

    def clear_selection(self):
        for button in self.selected_bubbles:
            button.uncheck()
        self.selected_bubbles = []
           
    def load_previous_image(self):
        if self._finish_editing_mode():
            new_page = self.chapter.previous_page()
            if new_page:
                self.current_page = new_page
                self._setup_page()
        

    def load_next_image(self):
        if self._finish_editing_mode():
            new_page = self.chapter.next_page()
            if new_page:
                self.current_page = new_page
                self._setup_page()
                return True
        
    def _finish_editing_mode(self):
        if self.can_edit:
            reply = QMessageBox.question(
                        self,
                        "End Edit Mode",
                        f"You must finish editing before changing pages. End edit mode?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
            if reply == QMessageBox.StandardButton.Yes:
                self.edition_mode_button.setChecked(False)
                self.edit_mode(False)
                return True
            else:
                return False
        else:
            return True
            


    def detect_all_pages(self):
        self.detect_bubbles_button.setDisabled(True)
        for page in self.chapter.pages:
            self.current_page = page
            self.detect_bubbles()
        self.current_page = self.chapter.get_current_page()
        self._setup_page()
        
        

    def detect_page_bubbles(self):
        if self.current_page:
            self.detect_bubbles()
            self._setup_page()

    def batch_extract_text(self):
        if self._finish_editing_mode():
            for page in self.chapter.pages:
                self.current_page = page
                self.extract_text()
            self.current_page = self.chapter.get_current_page()
            self._setup_page()


    def add_segment(self):
        if not self.current_page:
            return

        text_box = TextBox(63, 618, 119, 746, "manual")
        

        segment = self.current_page.create_segment(text_box)
        rect = segment.button
        rect.set_segment(segment)
        rect.link_on_click(lambda checked, btn=rect: self.selected_bubble(btn))
        self.scene.addItem(rect)

    def add_bubble(self):
        self.add_segment()

    def reorder_segments(self):
        if not self.current_page:
            return
        self.current_page.automatic_sort()
        self._setup_page()

    def _update_edit_menu_position(self):
        if not self.edit_menu or not self.view:
            return

        margin = 12
        menu_width = 140
        menu_height = 100
        x = self.view.width() - menu_width - margin
        y = margin
        self.edit_menu.setGeometry(x, y, menu_width, menu_height)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_edit_menu_position()

    def set_panel_zoom(self,panel):
        if not panel:
            print("Panel null")

        # Extract panel coordinates
        x = panel.text_box.xmin
        y = panel.text_box.ymin
        w = panel.text_box.xmax - panel.text_box.xmin
        h = panel.text_box.ymax - panel.text_box.ymin

        # Define panel target rectangle in scene coordinates
        panel_rect = QRectF(x, y, w, h)

        # Optional: Add padding around panel (e.g., 20px) so borders aren't clipped
        margin = 20
        panel_rect_padded = panel_rect.adjusted(-margin, -margin, margin, margin)

        # Scale view to fit the panel area
        self.view.fitInView(panel_rect_padded, Qt.AspectRatioMode.KeepAspectRatio)

        # Sync internal zoom factor with current transform matrix
        self.zoom_factor = self.view.transform().m11()
        self.status_label.setText(f"Focused on panel | Zoom: {self.zoom_factor:.2f}x")


    def edit_mode(self, checked):
        self.can_edit = checked
        if self.current_page:
            self.current_page.set_edit_mode(checked)
        if self.edit_menu:
            self.edit_menu.setVisible(checked)
            self.edit_menu.raise_()
            self._update_edit_menu_position()

    def prompt_and_delete_segment(self, button):
        print("Entre")
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete Segment #{button.number}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:    
            self.scene.removeItem(button)
            self.controller.delete_segment(button.segment)
            self.current_page.delete_segment(button.segment)

    def combine_segments(self, button):
        print("Combine")