from chapter_window import ChapterWindow
from create_chapter_window import CreateChapterWindow
from data_structure.chapter import Chapter
from data_structure.page import Page
from project_storage import safe_name
from project_window import ProjectWindow
from PyQt6.QtWidgets import QDialog

from tool_windows.termbase_panel import TermbasePanel

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
        self.project_window.edit_requested.connect(self.edit_project_info)
        self.project_window.delete_project_requested.connect(self.delete_project)
        self.project_window.show()

    def get_thubnail_path(self,chapter):
        print(self.storage.get_image_path(chapter))
        return self.storage.get_image_path(chapter)
    def add_chapter(self):
        create_chapter_window = CreateChapterWindow(existing_numbers=[c.number for c in self.project.chapters])
        data = create_chapter_window.exec()
        if data == QDialog.DialogCode.Accepted:
            ch_data = create_chapter_window.get_chapter_data()
            chapter = self.create_project_chapter(ch_data)
            #self.project_window.close()
            self.open_chapter_window(chapter)
        return None

    def create_project_chapter(self, project_data):
        number = project_data["number"]
        chapter = Chapter(self.project,self.project.series_name, project_data["name"], number, self.project.target_language)
        chapter.termbase = self.project.termbase
        chapter.translation_memory = self.project.translation_memory
        relative_path = self.project.add_chapter(chapter)
        self.storage.add_chapter(self.storage.chapter_dir(relative_path))
        self.storage.write_json(f"{safe_name(self.project.project_name)}.romi", self.project.get_data())
        return chapter

    def delete_chapter(self, chapter):
        self.project.remove_chapter(chapter)
        self.loader.save_project(self.project)                # manifest first, as discussed
        #self.storage.delete_chapter_folder(chapter.id)         # then the folder (recycle bin)

    def rename_chapter(self, chapter, new_name):
        chapter.name = new_name
        self.project.update_chapter(chapter)
        self.loader.save_chapter(chapter)  # chapter.json now lists the new name

    def open_chapter(self, chapter_Entry):
        chapter = self.loader.load_chapter(self.project, chapter_Entry)
        self.open_chapter_window(chapter)

    def open_chapter_window(self, chapter):
        self.chapter_window = ChapterWindow(text_extractor=self.text_extractor, chapter=chapter, project_loader=self.loader, project_manager=self)

    def show_termbase_panel(self):
        termbase_panel = TermbasePanel(termbase=self.project.termbase)
        termbase_panel.show()
        

    def edit_project_info():
        print("edit")

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
        self.project.translation_memory.save_checked_segments(segments)