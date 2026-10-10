from data_structure.text_box import TextBox
from data_structure.segment import Segment
from image_area_widgets.combine_arrow import CombineArrow

class SegmentCombined(Segment):
    
    def __init__(self, page, segment_nro):
        super().__init__(page, segment_nro)
        self.next_segment = None
        self.next_arrow = None

    def set_next_segment(self, next_segment):
        self.next_segment = next_segment
        self.next_arrow = CombineArrow(self,next_segment)

    def set_nro(self, nro):
        super().set_nro(nro)
        if self.next_segment:
            return self.next_segment.set_nro(nro+1)
        else:
            return nro

    def get_data(self):
        data = super().get_data()
        child = self.get_child()
        data["next_segment"] = child.get_data() if child else None
        return data
    
    def load_data(self, data):
        super().load_data(data)
        
        if data["next_segment"]["next_segment"]:
            next_segment = SegmentCombined(self.page, -1)
        else:
            next_segment = Segment(self.page, -1)
        next_segment.page = self.page
        if data["next_segment"]:
            next_segment.load_data(data["next_segment"])
        self.set_next_segment(next_segment)

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
        self.text_box.segment = self
        self.button = segment.button
        self.button.segment = self
        self.segment_box = segment.segment_box
        self.panel = segment.panel

    def set_edit_mode(self, value):
        super().set_edit_mode(value)
        if self.next_arrow:
            self.next_arrow.set_edit_mode(value)