
from pathlib import Path

from CATtools.termbase import Termbase
from aux_types.export_stategy import EXPORTERS
from data_structure.chapter import Chapter
import json

from PyQt6.QtWidgets import QDialog, QFileDialog, QMainWindow

from create_project_window import CreateProjectWindow
from PIL import Image

from data_structure.project import Project
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

        self.storage = ProjectStorage(root)
        self.storage.create_structure()

        project = Project(path=str(root), series_name=project_data["series_name"],
                        name=project_data["project_name"], source_language = project_data["source_language"], target_language=project_data["output_language"])
        project.termbase = Termbase(project_data["source_language"], project_data["output_language"])

        cover_src = project_data.get("cover_path")
        project.cover = self.storage.store_image(cover_src, self.storage.SHARED_DIR, new_name="cover") if cover_src else None

        self.storage.write_json("shared/termbase.json", {"schema_version": 1, **project.termbase.get_data()})
        self.storage.write_json(f"{safe_name(project.project_name)}.romi", project.get_data())
        return project
    
   

    def load_project(self):
        load_path = QFileDialog.getOpenFileName()
        if load_path[0]:
            self.project = self.load_project_chapter(load_path[0])
            return self.project
        
    def load_project_chapter(self, file_path):
        #Load project from file
        self.save_path = file_path
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.project = Chapter(
            series_name=data["series_name"],
            name=data["name"],
            number=data["number"]
        )
        self.project.load_chapter(data)
        return self.project

    def save_project(self):
        print("Saving project...")
        print(self.save_path)
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump(self.project.get_data(), f)
            
    def save_chapter(self, chapter):
        path = chapter.path
        chapter_data_path = Path(self.storage.chapter_dir(path)) / f"{self.CHAPTER_DATA}.json"
        self.storage.write_json(chapter_data_path, chapter.get_data())

    def export_translation(self, export_path, exporter_name="Excel (structured)", data=None):
        exporter = EXPORTERS[exporter_name]

        # the extension comes from the exporter, not hardcoded
        ext = "." + exporter.extension
        if not export_path.endswith(ext):
            export_path += ext

        # reuse the data the preview already showed, if there is one
        if data is None:
            data = exporter.build(self.project)

        exporter.export(data, export_path)
        print(f"Translation exported to {export_path}")
        return export_path
