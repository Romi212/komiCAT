from PyQt6.QtWidgets import QMenu, QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import Qt
from data_structure.segment_list import SegmentList
from text_area_widgets.combined_container import CombinedContainer
from text_area_widgets.segment_box import SegmentBox

class PageContainer(QWidget):
    def __init__(self, page, parent=None):
        super().__init__(parent)
        self.page = page
        
        # Enable receiving drop events
        self.setAcceptDrops(True)
        self.active_drag_widget = None  

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10)

        self.page_label = QLabel("--------------------------- Page " + self.page.page_name + " ----------------------------------")
        self.page_label.setStyleSheet("font-weight: bold; border: none;")
        self.layout.insertWidget(0, self.page_label)

    def addSegment(self, segment_box):
        self.layout.insertWidget(segment_box.get_index()+1, segment_box)
        segment_box.set_drag_callback(self.set_active_drag_widget)  

    def addCombinedSegment(self, container, head_segment):
        self.layout.insertWidget(head_segment.get_index() + 1, container)
        container.set_container_drag_callback(self.set_active_drag_widget) 

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
        ordered_segments = SegmentList()
        index = 1
        for i in range(1,self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            
            if widget.segment:
                segment = widget.segment
                index = segment.set_nro(index) +1
                ordered_segments.add_segment(segment)
        self.page.update_segments(ordered_segments)

    def remove_segment(self, segment):
        self.layout.removeWidget(segment)

    def set_edit_mode(self, page, enabled: bool):
        if page.number == self.page.number:
            for container in self.findChildren(CombinedContainer):
                container.set_edit_mode(enabled)
            if not enabled:
                self.sync_logical_segments()
            