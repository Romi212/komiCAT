from chapter_window import ChapterWindow
from create_chapter_window import CreateChapterWindow
from data_structure.chapter import Chapter
from project_window import ProjectWindow
from PyQt6.QtWidgets import QDialog

class ProjectManager():
    def __init__(self, project, loader, text_extractor):
        self.project, self.loader, self.text_extractor = project, loader, text_extractor
        self.storage  = loader.storage
        self.project_window = ProjectWindow(project= self.project)
        self.project_window.chapter_add_requested.connect(self.add_chapter)       # your logic, then home.refresh()
        self.project_window.chapter_opened.connect(self.open_chapter_window)      # opens your existing ProjectWindow
        self.project_window.chapter_rename_requested.connect(self.rename_chapter)
        self.project_window.chapter_delete_requested.connect(self.delete_chapter)
        self.project_window.termbase_requested.connect(self.show_termbase_panel)
        self.project_window.edit_requested.connect(self.edit_project_info)
        self.project_window.delete_project_requested.connect(self.delete_project)
        self.project_window.show()

    def add_chapter(self):
        create_chapter_window = CreateChapterWindow()
        data = create_chapter_window.exec()
        if data == QDialog.DialogCode.Accepted:
            ch_data = create_chapter_window.get_project_data()
            chapter = self.create_project_chapter(ch_data)
            self.project_window.close()
            self.chapter_window = ChapterWindow(self.text_extractor,chapter,self.loader)
        return None

    def create_project_chapter(self, project_data):
        number = len(self.project.chapters)
        chapter = Chapter(self.project.series_name, project_data["chapter_name"], number, self.project.target_language)
        self.project.add_chapter(chapter)
        return chapter

    def delete_chapter(self, chapter):
        self.project.remove_chapter(chapter)
        self.loader.save_manifest(self.project)                # manifest first, as discussed
        self.storage.delete_chapter_folder(chapter.id)         # then the folder (recycle bin)

    def rename_chapter(self, chapter, new_name):
        chapter.name = new_name
        self.loader.save_manifest(self.project)

    def open_chapter_window(self, chapter):
        self.chapter_window = ChapterWindow(self.text_extractor, self.loader, chapter)

    def show_termbase_panel(self):
        print("TERMBASE")

    def edit_project_info():
        print("edit")

    def delete_project():
        print("delete")