

from PIL import Image

from CATtools.termbase import Termbase
from data_structure.page import Page


class Chapter:
    def __init__(self, project, series_name, name, number,language='es'):
        self.project = project
        self.name = name
        self.series_name = series_name
        self.number = number
        self.path = "ch"+str(number)
        self.pages = []
        self.current_page = 0
        self.language = language 
        self.termbase = None
        self.translation_memory = None


    def add_page(self, page):
        self.pages.append(page)


    def load_chapter(self, data):
        if "termbase" in data and data["termbase"]:
            self.termbase = Termbase(data["termbase"]["source_lan"], data["termbase"]["target_lan"])
            self.termbase.load_data(data["termbase"])
        for page_data in data["pages"]:
            page = Page(file_path=page_data["file_path"], chapter=self, number=len(self.pages))
            self.add_page(page)
            page.load_page(page_data)
            

    def get_current_page(self):
        if self.pages:
            return self.pages[self.current_page]
        return None
    
    def next_page(self):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            return self.pages[self.current_page]
        return None
    
    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            return self.pages[self.current_page]
        return None
    

    def get_data(self):
        return {
            "name": self.name,
            "number": self.number,
            "termbase": self.termbase.get_data() if self.termbase else None,
            "pages": [page.get_data() for page in self.pages]
        }
    
    def get_translation_text(self):
        translation_text = f"{self.series_name} - Chapter {self.number}: {self.name}\n\n"
        for page in self.pages:
            translation_text += page.get_translation_text()
        return translation_text
    
    def set_current_page(self, page):
        self.current_page = self.pages.index(page)

    def get_termbase(self):
        if self.termbase is None:
            self.termbase = Termbase("jp", self.language)
        return self.termbase

    def get_tm(self):
        if not self.translation_memory:
            self.translation_memory = self.project.translation_memory
        return self.translation_memory