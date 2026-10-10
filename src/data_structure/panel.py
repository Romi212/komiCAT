
from data_structure.segment import Segment
from data_structure.segment_combined import SegmentCombined
from data_structure.segment_list import SegmentList
from data_structure.text_box import TextBox


class Panel:

    def __init__(self, text_box):
        self.text_box = text_box
        self.segments = []
        self.nro = 0

    def contains_segment(self, segment):
        return self.text_box.intersects(segment.text_box)

    def add_segment(self, segment):
        if not segment in self.segments:
            self.segments.append(segment)

    def sort_segments(self, base_index):
        segment_list = SegmentList()
        segment_list.append_from_array(self.segments)
        index, seg_list = segment_list.sort_segments(base_index)
        self.segments.sort(key=lambda seg: seg.nro)
        return index, seg_list

        

    def get_data(self):
        return {
                    "bounds": {"xmin": self.text_box.xmin, "ymin": self.text_box.ymin, "xmax": self.text_box.xmax, "ymax": self.text_box.ymax},
                    "nro": self.nro  
                }

    def load_panel(self, panel_data, page):
        self.text_box = TextBox(
                            panel_data["bounds"]["xmin"],
                            panel_data["bounds"]["xmax"],
                            panel_data["bounds"]["ymin"],
                            panel_data["bounds"]["ymax"], 
                            "panel"
                        )
        self.nro = panel_data["nro"]
        
    def load_segments(self, panel_data, page):
        self.text_box = TextBox(
                    panel_data["bounds"]["xmin"],
                    panel_data["bounds"]["xmax"],
                    panel_data["bounds"]["ymin"],
                    panel_data["bounds"]["ymax"], 
                    "panel"
                )
        self.nro = panel_data["nro"]
        segments_data = panel_data["segments"]
        for segment_data in segments_data:
            if segment_data["next_segment"]:
                print("loading combined")
                segment = SegmentCombined(self, segment_data["nro"])
            else:
                segment = Segment(self, segment_data["nro"])
            segment.page = page
            segment.panel = self
            segment.load_data(segment_data)
            self.segments.add_segment(segment)
            
        

    def delete_segment(self,segment):
        if segment in self.segments:
            self.segments.remove(segment)