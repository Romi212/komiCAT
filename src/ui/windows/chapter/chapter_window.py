import sys
from PyQt6.QtWidgets import QApplication, QDialog, QFileDialog, QMainWindow, QMessageBox, QSplitter, QVBoxLayout, QWidget, QMenuBar
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence

from data_structure.page import Page
from data_structure.segment_combined import SegmentCombined
from ui.windows.project.create_project_window import CreateProjectWindow
from ui.windows.chapter.image_area_widgets.image_viewer import ImageViewer
from storage.project_loader import ProjectLoader
from ui.windows.chapter.text_area_widgets.text_viewer import TextViewer
from data_structure.chapter import Chapter
from ui.windows.tools.termbase_panel import TermbasePanel
from ui.windows.tools.translation_memory_panel import TranslationMemoryPanel

class ChapterWindow(QMainWindow):
    edit_mode_changed = pyqtSignal(Page, bool)
    def __init__(self, text_extractor=None, chapter=None, project_loader=None, project_manager= None):
        super().__init__()
        
        self.text_extractor = text_extractor;
        self.project_loader = project_loader;
        self.project_manager = project_manager
        
        # Create main window
        
        self.setWindowTitle("KomiCAT")
        self.resize(1600, 900)

        #Create menu bar
        self.menu_bar = QMenuBar(self)
        file_menu = self.menu_bar.addMenu("File")
        #Save project button
        create_action = file_menu.addAction("New Project")
        create_action.triggered.connect(self.create_new_project)

        save_action = file_menu.addAction("Save Project")
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_project)

        #Load project button
        load_action = file_menu.addAction("Load Project")
        load_action.triggered.connect(self.load_project)

        project_menu = self.menu_bar.addMenu("Project")

        export_menu = project_menu.addMenu("Export Translation")
        txt_export_action = export_menu.addAction("txt")
        txt_export_action.triggered.connect(lambda: self.export_translation("Plain text"))

        excel_export_action = export_menu.addAction("excel")
        excel_export_action.triggered.connect(lambda: self.export_translation("Excel (structured)"))

        termbase_action = project_menu.addAction("Termbase")
        termbase_action.triggered.connect(self.show_termbase)

        tm_action = project_menu.addAction("Translation Memory")
        tm_action.triggered.connect(self.show_tm)
        

        # Create central widget with splitter
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
       

        
        # Create viewers
        self.text_viewer = TextViewer(controller=self, chapter=chapter)
        self.image_viewer = ImageViewer(controller=self, chapter=chapter, text_extractor=self.text_extractor)
        
        self.set_up_chapter(chapter)
        

        open_images = project_menu.addAction("Open Images")
        open_images.triggered.connect(self.image_viewer.open_images)

        view_menu = self.menu_bar.addMenu("View")
        next_action = QAction("Next page", self)
        next_action.setShortcut(QKeySequence("Alt+Right"))
        next_action.triggered.connect(self.image_viewer.load_next_image)
        view_menu.addAction(next_action)

        prev_action = QAction("Previous page", self)
        prev_action.setShortcut(QKeySequence("Alt+Left"))
        prev_action.triggered.connect(self.image_viewer.load_previous_image)
        view_menu.addAction(prev_action)
        
        # Add to splitter
        splitter.addWidget(self.text_viewer)
        splitter.addWidget(self.image_viewer)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([1, 1])
        self.text_viewer.setMinimumWidth(400)
        
        
        layout.setMenuBar(self.menu_bar)
        layout.addWidget(splitter)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.show()
       

    def set_up_chapter(self, chapter):
        self.chapter = chapter
        self.termbase = self.chapter.get_termbase()
        self.translation_memory = self.chapter.translation_memory
        self.termbase_panel = TermbasePanel(self.termbase, self)
        self.tm_panel = TranslationMemoryPanel(self.translation_memory, self)
        self.image_viewer.load_chapter(self.chapter)
        self.text_viewer.load_chapter(self.chapter)

    def extracted(self, page, segments):
        self.text_viewer.add_extracted_segments(page,segments)


    def save_project(self):
        self.project_manager.save_chapter(self.chapter)
        self.image_viewer.status_label.setText("Project saved successfully!")   
        return True

    def load_project(self):

        chapter = self.project_loader.load_project()
        if(chapter):
            self.set_up_chapter(chapter)
        #TODO ELSE TIRAR ERROR CANT OPEN PROJECT

    def export_translation(self, exporter_name="Excel (structured)"):
        if not self.chapter:
            return

        extension = "txt" if exporter_name == "Plain text" else "xlsx"
        default_name = f"{self.chapter.name or 'translation'}.{extension}"
        export_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Translation",
            default_name,
            f"Text files (*.txt);;Excel files (*.xlsx)"
        )
        if not export_path:
            return

        self.project_loader.export_translation(self.chapter, export_path, exporter_name)

    def show_termbase(self):
        self.termbase_panel.show()
        self.termbase_panel.raise_()
        self.termbase_panel.activateWindow()

    def show_tm(self):
            self.tm_panel.show()
            self.tm_panel.raise_()
            self.tm_panel.activateWindow()

    def create_new_project(self):
        
        chapter = self.project_loader.create_new_project()
        if(chapter):
            self.set_up_chapter(chapter)
        #TODO: ELSE mostrar error creando nuevo

    def set_current_page(self, page, change_focus= True):
        self.chapter.set_current_page(page)
        self.image_viewer._setup_page(change_focus)

    def set_panel_zoom(self,panel):
        self.image_viewer.set_panel_zoom(panel)

    def delete_segment(self, segment):
        self.text_viewer.delete_segment(segment)

    def change_edit_mode(self, page, can_edit):
            #page.set_edit_mode(can_edit)
            self.edit_mode_changed.emit(page, can_edit)
            if not can_edit:
                self.text_viewer.update_tab_order(page)
            else:
                page.set_edit_mode(can_edit)
                
    def page_changed(self, page):
        self.text_viewer.focus_page(page)

    def open_images(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Open Image File",
            "",
            "Image files (*.png *.jpg *.jpeg *.gif *.bmp *.ico);;All files (*)"
        )
        if not paths:
            return False
        return self.project_manager.open_images(self.chapter, paths)

    def save_checked_segments(self, segments):
        print(segments)
        self.project_manager.update_translation_memory(segments)

    def closeEvent(self, event):

        Btn = QMessageBox.StandardButton
        reply = QMessageBox.question(
            self,
            "Unsaved changes",
            "Do you want to save your changes before closing?",
            Btn.Save | Btn.Discard | Btn.Cancel,
            Btn.Save,
        )

        if reply == Btn.Save:
            if self.save_project():
                self.project_manager.close_chapter_window(self.chapter.number)
                event.accept()
            else:
                event.ignore()      # save failed or was cancelled, stay open
        elif reply == Btn.Discard:
            self.project_manager.close_chapter_window(self.chapter.number)
            event.accept()
        else:
            event.ignore()