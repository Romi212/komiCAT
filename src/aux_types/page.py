import os


class Page:
    def __init__(self, file_path=None, image=None):
        
        self.file_path = file_path
        self.image = image
        self.page_name = os.path.basename(file_path)
        self.segments = []
        
