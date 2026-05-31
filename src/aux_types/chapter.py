

class Chapter:
    def __init__(self,  series_name, name, number):
        self.name = name
        self.series_name = series_name
        self.number = number
        self.pages = []
        self.current_page = 0


    def add_page(self, page):
        self.pages.append(page)

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