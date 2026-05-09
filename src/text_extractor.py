import PIL.Image

from manga_ocr import MangaOcr

class TextExtractor:

    def __init__(self):
        self.mocr = MangaOcr()

    def extract_text(self, image):
        text = self.mocr(image)
        return text
