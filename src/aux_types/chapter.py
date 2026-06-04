

from PIL import Image

from aux_types.page import Page


class Chapter:
    def __init__(self,  series_name, name, number):
        self.name = name
        self.series_name = series_name
        self.number = number
        self.pages = []
        self.current_page = 0


    def add_page(self, page):
        self.pages.append(page)


    def load_chapter(self, data):
        for page_data in data["pages"]:
            image = Image.open(page_data["file_path"])
            page = Page(file_path=page_data["file_path"], image=image, chapter=self)
            self.add_page(page)
            page.load_segments(page_data["segments"])
            

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
            "series_name": self.series_name,
            "number": self.number,
            "pages": [page.get_data() for page in self.pages]
        }