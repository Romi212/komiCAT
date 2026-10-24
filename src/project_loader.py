
from pathlib import Path

from CATtools.termbase import Termbase
from CATtools.translation_memory import TranslationMemoryDB
from aux_types.export_stategy import EXPORTERS
from data_structure.chapter import Chapter
import json

from PyQt6.QtWidgets import QDialog, QFileDialog, QMainWindow

from create_project_window import CreateProjectWindow
from PIL import Image

from data_structure.project import ChapterEntry, Project
from project_storage import ProjectStorage, safe_name


SCHEMA_VERSION = 1


class ProjectLoader:
    CHAPTER_DATA = "chapter_data"

    def __init__(self):
        self.project = None
        self.save_path = ""
        self.storage = None


    def create_new_project(self):
        self.create_project_window = CreateProjectWindow()
        data = self.create_project_window.exec()
        if data == QDialog.DialogCode.Accepted:
            project_data = self.create_project_window.get_project_data()
            self.project = self.create_project(project_data)
            return self.project
        return None

    def create_project(self, project_data):
        root = Path(project_data["path"]) / safe_name(project_data["project_name"])
        if root.exists() and any(root.iterdir()):
                            raise FileExistsError(f"The folder already exists and is not empty:\n{root}")
                
        self._create_storage(root)
        project_data["path"] = root
        project = Project(path=str(project_data["path"]), series_name=project_data["series_name"],
                        name=project_data["project_name"], source_language = project_data["source_language"], target_language=project_data["target_language"])
        project.termbase = Termbase(project_data["source_language"], project_data["target_language"])
        project.translation_memory = TranslationMemoryDB(self.storage.resolve(self.storage.TRANSLATION_MEMORY))
        cover_src = project_data.get("cover_path")
        project.cover = self.store_new_cover(cover_src)
        self.save_project(project)
        return project

    def store_new_cover(self, cover_src):
        self.storage.delete_old_cover()
        return self.storage.store_image(cover_src, self.storage.SHARED_DIR, new_name="cover") if cover_src else None
        
    def _create_storage(self,root):
        
        self.storage = ProjectStorage(root)
        self.storage.create_structure()

    

    def load_project(self, load_path = None):
        if load_path is None:
            load_path, _ = QFileDialog.getOpenFileName(None, "Open project", "", "KomiCAT project (*.romi)")
        if not load_path:
            return
        root = Path(load_path).parent
        project_name = Path(load_path).stem
        self._create_storage(root)
        project_data = self.storage.read_json(project_name+".romi")
        cover_path = self.storage.get_cover_image_path()
        project = Project(str(root), name = project_name, cover_image=cover_path)
        project.load_project(project_data)
        self.load_shared(project)
        self.project = project
        return project
        
    def load_shared(self, project):
        termbase_data = self.storage.read_json(Path(self.storage.SHARED_DIR) / safe_name("termbase.json"))
        project.termbase = Termbase(project.source_language, project.target_language)
        project.termbase.load_data(termbase_data)
        project.translation_memory = TranslationMemoryDB(self.storage.resolve(self.storage.TRANSLATION_MEMORY))


    def load_chapter(self, project, chapter):
         rel_path = Path(self.storage.CHAPTERS_DIR) / chapter.path / f"{self.CHAPTER_DATA}.json"
         chapter_data = self.storage.read_json(rel_path)
         loaded_chapter = Chapter(project,project.series_name, chapter.name, chapter.number, project.target_language)
         loaded_chapter.load_chapter(chapter_data)
         loaded_chapter.termbase = project.termbase
         loaded_chapter.translation_memory = project.translation_memory
         return loaded_chapter
         
    def save_project(self, project):
        print("Saving project...")
        self.storage.write_json(f"{safe_name(project.project_name)}.romi", project.get_data())
        self.storage.write_json("shared/termbase.json", {"schema_version": 1, **project.termbase.get_data()})
        
            
    def save_chapter(self, chapter):
        path = chapter.path
        chapter_data_path = Path(self.storage.chapter_dir(path)) / f"{self.CHAPTER_DATA}.json"
        self.storage.write_json(chapter_data_path, chapter.get_data())
        self.save_project(self.project)  # save the project manifest too, as it lists the chapters 

    def export_translation(self, chapter, export_path, exporter_name="Excel (structured)", data=None):
        exporter = EXPORTERS[exporter_name]

        # the extension comes from the exporter, not hardcoded
        ext = "." + exporter.extension
        if not export_path.endswith(ext):
            export_path += ext

        # reuse the data the preview already showed, if there is one
        if data is None:
            data = exporter.build(chapter)

        exporter.export(data, export_path)
        print(f"Translation exported to {export_path}")
        return export_path
