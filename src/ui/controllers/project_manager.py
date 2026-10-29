from ui.windows.chapter.chapter_window import ChapterWindow
from ui.windows.chapter.create_chapter_window import CreateChapterWindow
from data_structure.chapter import Chapter
from data_structure.page import Page
from CATtools.spell_checker import SpellChecker
from CATtools.jp_dictionaries import JPDictionary
from storage.project_storage import safe_name
from ui.windows.project.project_window import ProjectWindow
from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import Qt
from ui.windows.tools.termbase_panel import TermbasePanel
from ui.windows.tools.translation_memory_panel import TranslationMemoryPanel
from errors import KomiError
from ui.windows.error_window import ErrorWindow

import functools, logging
logger = logging.getLogger(__name__)

def handle_errors(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except KomiError as e:
            logger.warning("%s failed", func.__name__, exc_info=True)
            ErrorWindow.show_error(self.project_window, e)
    return wrapper

class ProjectManager():
    def __init__(self, project, loader, text_extractor):
        self.project, self.loader, self.text_extractor = project, loader, text_extractor
        self.storage  = loader.storage
        self.project_window = ProjectWindow(project= self.project, thumbnail_path=self.get_thubnail_path)
        self.project_window.chapter_add_requested.connect(self.add_chapter)       # your logic, then home.refresh()
        self.project_window.chapter_opened.connect(self.open_chapter)      # opens your existing ProjectWindow
        self.project_window.chapter_rename_requested.connect(self.rename_chapter)
        self.project_window.chapter_delete_requested.connect(self.delete_chapter)
        self.project_window.termbase_requested.connect(self.show_termbase_panel)
        self.project_window.memory_requested.connect(self.show_translation_memory_panel)
        self.project_window.edit_requested.connect(self.edit_project_info)
        self.project_window.delete_project_requested.connect(self.delete_project)
        self.project_window.close_project_requested.connect(self.close_all_chapters)
        self.project_window.show()
        self.open_chapters = {}

    def get_thubnail_path(self,chapter):
        print(self.storage.get_image_path(chapter))
        return self.storage.get_image_path(chapter)

    @handle_errors
    def add_chapter(self):
        create_chapter_window = CreateChapterWindow(existing_numbers=[c.number for c in self.project.chapters])
        data = create_chapter_window.exec()
        if data == QDialog.DialogCode.Accepted:
            #TODO try catch y eliminar si no se creó correctamente
            ch_data = create_chapter_window.get_chapter_data()
            chapter = self.create_project_chapter(ch_data)
            #self.project_window.close()
            self.create_chapter_window(chapter)
            self.project_window.refresh()
        return None
    
    def create_project_chapter(self, project_data):
        number = project_data["number"]
        chapter = self.create_chapter_object(project_data["name"], number)
        relative_path = self.project.add_chapter(chapter)
        self.storage.add_chapter(self.storage.chapter_dir(relative_path))
        self.storage.write_json(f"{safe_name(self.project.project_name)}.romi", self.project.get_data())
        return chapter

    def create_chapter_object(self, name, number):
        chapter = Chapter(self.project,self.project.series_name, name, number, self.project.target_language)
        chapter.termbase = self.project.termbase
        chapter.translation_memory = self.project.translation_memory
        chapter.spell_checker = self.project.spell_checker
        chapter.jp_dict = self.project.jp_dict
        return chapter

    @handle_errors
    def delete_chapter(self, chapter):
        self.project.remove_chapter(chapter)
        self.loader.save_project(self.project)               
        #self.storage.delete_chapter_folder(chapter.id)     
        self.project_window.refresh()    
    @handle_errors
    def rename_chapter(self, chapter, new_name):
        chapter.name = new_name
        self.project.update_chapter(chapter)
        self.loader.save_project(self.project) 
        self.project_window.refresh()
    @handle_errors
    def open_chapter(self, chapter_Entry):
        window = self.open_chapters.get(chapter_Entry.number)
        
        if window is not None:
            # Already open: restore if minimized, then bring to front
            if window.isMinimized():
                window.setWindowState(
                    window.windowState() & ~Qt.WindowState.WindowMinimized
                    | Qt.WindowState.WindowActive
                )
            window.show()
            window.raise_()
            window.activateWindow()
            return

        chapter = self.create_chapter_object(chapter_Entry.name, chapter_Entry.number)
        chapter = self.loader.load_chapter( chapter)
        window = self.create_chapter_window(chapter)
        

    def create_chapter_window(self, chapter):
        
        window = ChapterWindow(
            text_extractor=self.text_extractor,
            chapter=chapter,
            project_loader=self.loader,
            project_manager=self,
        )
        
        window.show()
        self.open_chapters[chapter.number] = window

    def close_chapter_window(self, chapter_number):
        self.open_chapters.pop(chapter_number)
    def show_termbase_panel(self):
        termbase_panel = TermbasePanel(termbase=self.project.termbase)
        termbase_panel.show()
    def show_translation_memory_panel(self):
        tm_panel = TranslationMemoryPanel(tm_db=self.project.translation_memory, parent=self.project_window)
        tm_panel.show()
        tm_panel.raise_()
        tm_panel.activateWindow()
    @handle_errors
    def edit_project_info(self, data, cover_path):
        if cover_path:
            self.loader.store_new_cover(cover_path)
        self.project.load_project(data)
        self.loader.save_project(self.project)

    def delete_project():
        print("delete")

    def open_images(self, chapter, src_paths):
        start = max((p.number for p in chapter.pages), default=-1) + 1   # next free file number
        stored = self.storage.store_chapter_images(chapter.path, src_paths, start_at=start)

        new_pages = []
        for entry in stored:
            page = Page(file_path=str(self.storage.resolve(entry["file"])),
                        rel_path=entry["file"],
                        chapter=chapter,
                        number=len(chapter.pages),
                        original_name=entry["original_name"])
            chapter.add_page(page)
            new_pages.append(page)

        #self.loader.save_chapter(chapter)        # chapter.json now lists the new pages
        return new_pages

    def save_chapter(self, chapter):
        self.loader.save_chapter(chapter)

    def update_translation_memory(self, segments):
        valid_segments = []
        for segment in segments:
            segment.set_confirmed(True)
            context = str({"chapter": segment.page.chapter, "page": segment.page.number})
            valid_segments.append((segment.source_text, segment.translation, context))
        self.project.translation_memory.save_checked_segments(valid_segments)

    def close_all_chapters(self):
         
        for window in list(self.open_chapters.values()):
            window.close()

        if not self.open_chapters:
            self.project_window.close()
