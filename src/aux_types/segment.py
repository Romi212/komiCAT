
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

    def text_extracted(self, text):
        self.source_text = text

    def update_source_text(self, new_text):
        self.source_text = new_text
        if self.segment_box:
            self.segment_box.set_japanese_text(new_text)

    def show_focus(self, focused):
        self.text_box_button_proxy.widget().set_focus(focused)