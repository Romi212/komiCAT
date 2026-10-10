from PyQt6.QtWidgets import QMenu, QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import Qt
from data_structure.segment_combined import SegmentCombined
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

        self.page_label = QLabel("---------------------------  " + self.page.page_name + " ----------------------------------")
        self.page_label.setObjectName("PageDivisionLabel")
        self.layout.insertWidget(0, self.page_label)
          
        
        self.combine_highlight = QWidget(self)
        self.combine_highlight.setFixedHeight(6)
        self.combine_highlight.hide()
        self.combine_highlight.setCursor(Qt.CursorShape.PointingHandCursor)
        self.combine_highlight.setObjectName("combineHighlight")

        self._hover_pair = None  # (top_widget, bottom_widget) currently highlighted

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        pair, gap_y, gap_height = self._find_gap_at(pos)

        if pair:
            self._hover_pair = pair
            self.combine_highlight.setGeometry(10, gap_y, self.width() - 20, gap_height)
            self.combine_highlight.show()
        else:
            self._hover_pair = None
            self.combine_highlight.hide()

        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self._hover_pair = None
        self.combine_highlight.hide()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self._hover_pair and self.combine_highlight.geometry().contains(event.position().toPoint()):
            top, bottom = self._hover_pair
            self.combine_adjacent(top, bottom)
        super().mousePressEvent(event)

    def combine_adjacent(self,top, bottom):
        if isinstance(top,CombinedContainer):
            top.addChild(bottom)
        else:
            index = self.layout.indexOf(top)
            head_segment = SegmentCombined(None,-1)
            head_segment.clone_segment(top.segment)
            top.segment = head_segment
            container = CombinedContainer(top)
            container.addChild(bottom)
            head_segment.set_next_segment(bottom.segment)
            
            self.layout.insertWidget(index, container)
            container.set_combine_callback(self.decombine_segments)
            container.set_container_drag_callback(self.set_active_drag_widget) 
            self.layout.removeWidget(top)
        self.layout.removeWidget(bottom)

    def _find_gap_at(self, pos):
        """Return ((top_widget, bottom_widget), gap_y, gap_height) if pos.y() sits in a gap, else (None, 0, 0)."""
        widgets = [
            self.layout.itemAt(i).widget()
            for i in range(self.layout.count())
            if self.layout.itemAt(i).widget() is not self.page_label
        ]

        margin = self.layout.spacing()
        for i in range(len(widgets) - 1):
            top, bottom = widgets[i], widgets[i + 1]
            gap_top = top.geometry().bottom()
            gap_bottom = bottom.geometry().top()
            if gap_top <= pos.y() <= gap_bottom:
                return (top, bottom), gap_top, gap_bottom - gap_top

        return None, 0, 0
    def addSegment(self, segment_box):
        self.layout.insertWidget(segment_box.get_index()+1, segment_box)
        segment_box.set_drag_callback(self.set_active_drag_widget)  

    def addCombinedSegment(self, container, head_segment):
        self.layout.insertWidget(head_segment.get_index() + 1, container)
        container.set_combine_callback(self.decombine_segments)
        container.set_container_drag_callback(self.set_active_drag_widget) 

    def decombine_segments(self, container):
        segs = container.segment_boxes
        index = self.layout.indexOf(container)
        self.layout.removeWidget(container)
        container.setParent(None)
        for seg in segs:
            if(seg.segment.get_child()):
                seg.segment.set_next_segment(None)
            self.layout.insertWidget(index,seg)
            index+=1
            
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
                if widget._edit_mode:
                    widget.set_edit_mode(False)
                segment = widget.segment
                index = segment.set_nro(index) +1
                ordered_segments.add_segment(segment)
        self.page.update_segments(ordered_segments)

    def remove_segment(self, segment):
        self.layout.removeWidget(segment)

    def set_edit_mode(self, page, enabled: bool):
        if page.number == self.page.number:
            self.setMouseTracking(enabled)
            for container in self.findChildren(CombinedContainer):
                container.set_edit_mode(enabled)
            if not enabled:
                self.sync_logical_segments()
            