from PIL import Image

from CATtools.termbase import Termbase

from dataclasses import dataclass, asdict

@dataclass
class ChapterEntry:

    number: int
    name: str
    path: str                      # relative, like "chapters/ch4"
    #use_series_termbase: bool = True
    #use_series_memory: bool = True

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def to_dict(self):
        return asdict(self)
    
class Project():
    def __init__(self,  path, series_name="Manga Title", name="my_project",source_language = "jp",target_language='es',cover_image = None):
            self.project_name = name
            self.path = path
            self.series_name = series_name
            self.target_language = target_language
            self.source_language = source_language 
            self.termbase = None
            self.term_memory = None
            self.translation_memory = None
            self.chapters = []
            self.cover_path = cover_image
            self.cover = self.cover_path
            


    def add_chapter(self, chapter):
        """Accepts a Chapter (when creating) or a ChapterEntry (when loading)."""
        if any(e.number == chapter.number for e in self.chapters):
            raise ValueError(f"Chapter {chapter.number} already exists")
        entry = ChapterEntry(
            number=chapter.number, name=chapter.name,
            path=chapter.path,
            #use_series_termbase=getattr(chapter, "use_series_termbase", True),
            #use_series_memory=getattr(chapter, "use_series_memory", True),
        )
        self.chapters.append(entry)
        return entry.path

    def remove_chapter(self, chapter):
        self.chapters = [e for e in self.chapters if e.number != chapter.number]

    def update_chapter(self, chapter):
        for i, e in enumerate(self.chapters):
            if e.number == chapter.number:
                self.chapters[i] = ChapterEntry(
                    number=chapter.number, name=chapter.name,
                    path=chapter.path,
                    #use_series_termbase=getattr(chapter, "use_series_termbase", True),
                    #use_series_memory=getattr(chapter, "use_series_memory", True),
                )
                return
        raise ValueError(f"Chapter {chapter.number} not found")
    
    def load_project(self, data):
        self.project_name = data["project_name"]  if "project_name" in data else self.project_name
        self.series_name = data["series_name"] if data["series_name"] else self.series_name
        self.target_language = data["target_language"] if data["target_language"] else self.target_language
        self.source_language = data["source_language"] if data["source_language"] else self.source_language
        self.cover_path = data["cover_path"] if "cover_path" in data else self.cover_path
        #self.cover = self.cover_path
        if "chapters" in data:
            self.chapters = [ChapterEntry.from_dict(d) for d in data.get("chapters", [])]
        
    def get_data(self):
            self.chapters.sort(key=lambda e: e.number)
            return {
                "project_name": self.project_name,
                "series_name": self.series_name,
                "target_language": self.target_language,
                "source_language": self.source_language,
                "path": self.path,
                "cover_path": self.cover_path,
                "chapters": [entry.to_dict() for entry in self.chapters]
            }        


    