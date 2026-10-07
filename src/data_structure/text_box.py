
from aux_types.segment_types import SEGMENT_TYPE_FORMAT, SegmentType


class TextBox:
    def __init__(self, xmin,xmax,ymin,ymax,label):
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax
        self.label = label
        self.text = ""
        self.index = 0
        self.text_type = SegmentType.BUBBLE
        if(label == "text_free"):
             self.text_type = SegmentType.FREE
        if(label == "sfx"):
             self.text_type = SegmentType.SFX

        self.text_type_format = SEGMENT_TYPE_FORMAT[self.text_type]
        

    def set_bubble_container(self, bubble_container):
        self.bubble_container = bubble_container

    def intersects_h(self, line):
            return (self.ymin < line) and (self.ymax > line)
    
    def intersects_v(self, line):
            return (self.xmin < line) and (self.xmax > line)
    def intersects(self, other):
        #Check if self intersects with another TextBox with a tolerance of 5 pixels
        tolerance = 1
        return not (self.xmax + tolerance < other.xmin or
                    self.xmin - tolerance > other.xmax or
                    self.ymax + tolerance < other.ymin or
                    self.ymin - tolerance > other.ymax)

    def update_text_type(self, type):
        self.text_type = type
        self.text_type_format = SEGMENT_TYPE_FORMAT[self.text_type]
        self.label = type