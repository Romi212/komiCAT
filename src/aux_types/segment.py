
from aux_types.text_box import TextBox
from aux_types.text_box_rect import TextBoxRect


class Segment:
    def __init__(self, page, segment_nro):
        self.page = page
        self.nro = segment_nro
        self.source_text = None
        self.translation = ""

        self.button = None
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
        self.button.set_focus(focused)

    def get_data(self):
        
        button = self.button
        return {
            "nro": self.nro,
            "is_extracted": button.has_been_extracted_flag,
            "bounds": {"xmin": button.text_box.xmin, "ymin": button.text_box.ymin, "xmax": button.text_box.xmax, "ymax": button.text_box.ymax},
            "label" : button.text_box.label,
            "source_text": self.source_text,
            "translation": self.translation,
            "next_segment": None
        }
    
    def load_data(self, data):
        self.nro = data["nro"]
        self.source_text = data["source_text"]
        self.translation = data["translation"]
        text_box = TextBox(
            data["bounds"]["xmin"],
            data["bounds"]["xmax"],
            data["bounds"]["ymin"],
            data["bounds"]["ymax"], 
            data["label"]
        )
        print(f"Loaded TextBox for Segment {self.nro}: ({text_box.xmin}, {text_box.ymin}, {text_box.xmax}, {text_box.ymax}) with label '{text_box.label}'")
        text_box.text = self.source_text
        button = TextBoxRect(
            text_box,
            alpha=0.6
        )
        self.button = button
        button.segment = self
        if data["is_extracted"]:
            button.has_been_extracted()

    def get_translation(self):
        if(self.nro == -1): 
            return ""
        return self.translation
    
    def get_child(self):
        return None