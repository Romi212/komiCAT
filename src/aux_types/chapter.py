

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


    def load_page(self, page_path, seg_data):
        image = Image.open(page_path)
        page = Page(file_path=page_path, image=image, chapter=self.chapter)
        self.add_page(page)
        page.load_segments(seg_data)
        

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
        data = f"Chapter: {self.name}\nSeries: {self.series_name}\nNumber: {self.number}\n"
        for page in self.pages:
            data += page.get_data() + "\n"
        return data