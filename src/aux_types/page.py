import os

from aux_types.segment import Segment


class Page:
    def __init__(self, file_path=None, image=None, chapter=None):
        
        self.file_path = file_path
        self.image = image
        self.page_name = os.path.basename(file_path)
        self.segments = []
        self.chapter = chapter
    

    def store_detected_bubbles(self, detected_bubbles, detected_text_bubbles, detected_free_text):
        self.detected_bubbles = detected_bubbles
        self.detected_text_bubbles = detected_text_bubbles
        self.detected_free_text = detected_free_text

    def create_segment(self, proxy):
        segment = Segment(self, -1, proxy)
        self.segments.append(segment)
        return segment