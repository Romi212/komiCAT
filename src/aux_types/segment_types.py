from enum import Enum
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QCursor

class SegmentType(Enum):
    BUBBLE = "text_bubble"
    FREE = "text_free"
    SFX = "sfx"


class SegmentTypeFormat:
    """Everything that varies per segment content-type, in one place."""
    def __init__(self, bg_color, border_color, export_tag, dictionary_key, box_display_class=None):
        self.bg_color = bg_color
        self.border_color = border_color
        self.export_tag = export_tag          # how this type is marked/formatted on export
        self.dictionary_key = dictionary_key  # which dict (jmdict vs a future sfx dict) to use
        self.box_display_class = box_display_class  # which SegmentBox subclass/variant renders it, if any


SEGMENT_TYPE_FORMAT = {
    SegmentType.BUBBLE: SegmentTypeFormat(
        bg_color=QColor(200, 0, 0, 50), border_color=QColor(255, 0, 0),
        export_tag=None,
        dictionary_key="jmdict",
    ),
    SegmentType.FREE: SegmentTypeFormat(
        bg_color=QColor(0, 0, 200, 50), border_color=QColor(0, 0, 255),
        export_tag=None,
        dictionary_key="jmdict",
    ),
    SegmentType.SFX: SegmentTypeFormat(
        bg_color=QColor(0, 200, 0, 50), border_color=QColor(0, 255, 0),
        export_tag="[SFX]",
        dictionary_key="sfx_dict",   # future distinct dictionary
        box_display_class="SFXSegmentBox",  # if display diverges enough to need its own class later
    ),
}