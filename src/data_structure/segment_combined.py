from data_structure.text_box import TextBox
from data_structure.segment import Segment

class SegmentCombined(Segment):
    
    def __init__(self, page, segment_nro):
        super().__init__(page, segment_nro)
        self.next_segment = None

    def set_next_segment(self, next_segment):
        self.next_segment = next_segment

    def set_nro(self, nro):
        super().set_nro(nro)
        if self.next_segment:
            return self.next_segment.set_nro(nro+1)
        else:
            return nro

    def get_data(self):
        
        return {
            "nro": self.nro,
            "is_extracted": self.source_text is not None,
            "bounds": {"xmin": self.text_box.xmin, "ymin": self.text_box.ymin, "xmax": self.text_box.xmax, "ymax": self.text_box.ymax},
            "label" : self.text_box.label,
            "source_text": self.source_text,
            "translation": self.translation,
            "next_segment": self.next_segment.get_data() if self.next_segment else None
        }
    
    def load_data(self, data):
        super().load_data(data)
        
        if data["next_segment"]["next_segment"]:
            self.next_segment = SegmentCombined(self.page, -1)
        else:
            self.next_segment = Segment(self.page, -1)
        if data["next_segment"]:
            self.next_segment.load_data(data["next_segment"])

    def get_translation(self):
        if(self.nro == -1): 
            return ""
        translation = self.translation
        if self.next_segment:
            translation += " // " + self.next_segment.get_translation()
        return translation
    
    def get_child(self):
        return self.next_segment

    def clone_segment(self, segment):
        self.page = segment.page
        self.nro = segment.nro
        self.source_text = segment.source_text
        self.translation = segment.translation

        self.text_box = segment.text_box
        self.button = segment.button
        self.segment_box = segment.segment_box
        self.panel = segment.panel