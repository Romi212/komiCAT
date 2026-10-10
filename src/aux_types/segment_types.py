from enum import Enum
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QCursor

class SegmentType(Enum):
    BUBBLE  = ("text_bubble")
    FREE = ("text_free")
    SFX     = ("sfx")

    def __init__(self, key):
        self.key = key
        


class SegmentTypeFormat:
    """Everything that varies per segment content-type, in one place."""
    def __init__(self, export_tag, dictionary_key, box_display_class=None):
        self.export_tag = export_tag          # how this type is marked/formatted on export
        self.dictionary_key = dictionary_key  # which dict (jmdict vs a future sfx dict) to use
        self.box_display_class = box_display_class  # which SegmentBox subclass/variant renders it, if any


SEGMENT_TYPE_FORMAT = {
    SegmentType.BUBBLE: SegmentTypeFormat(
        
        export_tag=None,
        dictionary_key="jmdict",
    ),
    SegmentType.FREE: SegmentTypeFormat(
        
        export_tag=None,
        dictionary_key="jmdict",
    ),
    SegmentType.SFX: SegmentTypeFormat(
        
        export_tag="[SFX]",
        dictionary_key="sfx_dict",   # future distinct dictionary
        box_display_class="SFXSegmentBox",  # if display diverges enough to need its own class later
    ),
}