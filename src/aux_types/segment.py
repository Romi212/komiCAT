
class Segment:
    def __init__(self, page, segment_nro, proxy):
        self.page = page
        self.nro = segment_nro
        self.source_text = ""
        self.translation = ""

        self.text_box_button_proxy = proxy
        self.segment_box = None 

    def set_segment_box(self, segment_box):
        self.segment_box = segment_box
        self.source_text = segment_box.get_japanese_text()