from PyQt6.QtWidgets import QMenu, QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import Qt

from segment_box import SegmentBox

class PageContainer(QWidget):
    def __init__(self, page, parent=None):
        super().__init__(parent)
        self.page = page
        
        # Enable receiving drop events
        self.setAcceptDrops(True)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10)


    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-segmentbox"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-segmentbox"):
            event.acceptProposedAction()

    def dropEvent(self, event):
        dragged_box = getattr(event.source(), "segment_box", None)
        if not dragged_box or not isinstance(dragged_box, SegmentBox):
            return

        drop_y = event.position().toPoint().y()
        target_index = self._calculate_drop_index(drop_y)

        old_index = self.layout.indexOf(dragged_box)
        if old_index != -1 and old_index != target_index:
            # 1. Update UI layout
            self.layout.removeWidget(dragged_box)
            if target_index > old_index:
                target_index -= 1
            self.layout.insertWidget(target_index, dragged_box)

            # 2. Update logical data structure
            self.sync_logical_segments()

        event.acceptProposedAction()

    def _calculate_drop_index(self, drop_y):
        """Find target layout index based on mouse Y coordinate."""
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget_middle_y = widget.y() + (widget.height() // 2)
                if drop_y < widget_middle_y:
                    return i
        return self.layout.count()

    def sync_logical_segments(self):
        """Re-orders logical segments in self.page to match visual layout order."""
        ordered_segments = []
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, SegmentBox) and widget.segment:
                widget.segment.nro = i + 1  # Update number sequence
                ordered_segments.append(widget.segment)

        # Update pointers for linked list structures
        for i, seg in enumerate(ordered_segments):
            next_seg = ordered_segments[i + 1] if i + 1 < len(ordered_segments) else None
            if hasattr(seg, "set_child"):
                seg.set_child(next_seg)

        # Update root list if page uses a list
        if hasattr(self.page, "segments"):
            if isinstance(self.page.segments, list):
                self.page.segments = ordered_segments