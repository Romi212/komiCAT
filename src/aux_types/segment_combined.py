from aux_types.text_box import TextBox
from aux_types.text_box_button import TextBoxButton
from aux_types.segment import Segment

class SegmentCombined(Segment):
    
    def __init__(self, page, segment_nro, proxy):
        super().__init__(page, segment_nro, proxy)
        self.next_segment = None

    def set_next_segment(self, next_segment):
        self.next_segment = next_segment
    

    def get_data(self):
        
        if(self.text_box_button_proxy):
            button = self.text_box_button_proxy.widget()
        else:
            button = self.button
        return {
            "nro": self.nro,
            "is_extracted": button.has_been_extracted_flag,
            "bounds": {"xmin": button.text_box.xmin, "ymin": button.text_box.ymin, "xmax": button.text_box.xmax, "ymax": button.text_box.ymax},
            "label" : button.text_box.label,
            "source_text": self.source_text,
            "translation": self.translation,
            "next_segment": self.next_segment.get_data() if self.next_segment else None
        }
    
    def load_data(self, data):
        super().load_data(data)
        
        if data["next_segment"]["next_segment"]:
            self.next_segment = SegmentCombined(self.page, -1, None)
        else:
            self.next_segment = Segment(self.page, -1, None)
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