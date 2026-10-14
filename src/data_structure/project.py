from PIL import Image

from CATtools.termbase import Termbase


class Project():
    def __init__(self,  path, series_name="Manga Title", name="my_project",source_language = "jp",target_language='es',cover_image = None):
            self.project_name = name
            self.path = path
            self.series_name = series_name
            self.target_language = target_language
            self.source_language = source_language 
            self.termbase = None
            self.term_memory = None
            self.chapters = []
            self.cover_path = cover_image
            if self.cover_path:
                        self.cover = Image.open(self.cover_path)


    def add_chapter(self, chapter):
          path = ""+str(chapter.number) + "_" + chapter.name
          self.chapters.append([chapter.number, path, chapter.name])

    def load_project(self, data):
        self.project_name = data["project_name"]
        self.series_name = data["series_name"]
        self.target_language = data["target_language"]
        self.source_language = data["source_language"]
        self.cover_path = data["cover_path"]
        if self.cover_path:
            self.cover = Image.open(self.cover_path)
        for chapter in data["chapters"]:
            self.chapters.append([chapter["number"],chapter["path"],chapter["name"]])
        
    def get_data(self):
            return {
                "project_name": self.project_name,
                "series_name": self.series_name,
                "target_language": self.target_language,
                "source_language": self.source_language,
                "path": self.path,
                "cover_path": self.cover_path,
                "chapters": [{"number": chapter[0], "path": chapter[1], "name": chapter[2]} for chapter in self.chapters]
            }        