from PyQt6.QtWidgets import QMenu, QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import Qt
from text_area_widgets.segment_box import SegmentBox

class PageContainer(QWidget):
    def __init__(self, page, parent=None):
        super().__init__(parent)
        self.page = page
        
        # Enable receiving drop events
        self.setAcceptDrops(True)
        self.acttive_drag_widget = None  

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10)

        self.page_label = QLabel("--------------------------- Page " + self.page.page_name + " ----------------------------------")
        self.page_label.setStyleSheet("font-weight: bold; border: none;")
        self.layout.insertWidget(0, self.page_label)

    def addSegment(self, segment_box):
        self.layout.insertWidget(self.layout.count() , segment_box)
        segment_box.set_drag_callback(self.set_active_drag_widget)  

    def addCombinedSegment(self, container, head_segment):
        self.layout.insertWidget(self.layout.count() , container)
        head_segment.set_drag_callback(self.set_active_drag_widget)  

    def set_active_drag_widget(self, widget):
        """Set the currently dragged widget."""
        self.active_drag_widget = widget
    def dragEnterEvent(self, event):
        if self.active_drag_widget is not None:
            event.acceptProposedAction()

    def dropEvent(self, event):
        dragged_box = self.active_drag_widget
        if not dragged_box:
            return

        drop_y = event.position().toPoint().y()
        target_index = self._calculate_drop_index(drop_y)

        # Move widget in layout directly using Python pointer
        self.layout.removeWidget(dragged_box)
        self.layout.insertWidget(target_index, dragged_box)
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