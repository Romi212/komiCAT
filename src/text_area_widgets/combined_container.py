from PyQt6.QtWidgets import QHBoxLayout, QMenu, QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import Qt
from data_structure.segment_combined import SegmentCombined
from text_area_widgets.segment_box import DragHandle, SegmentBox

class CombinedContainer(QWidget):
    def __init__(self, segment_head, parent=None):
        super().__init__(parent)
        self.segment = segment_head
        self.segment_boxes = []
        self.segment_boxes.append(segment_head)

        self.setObjectName("combinedSegmentContainer")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("#combinedSegmentContainer { border: 2px solid #6e2130; border-radius: 5px; }")

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(5)
        self.layout.addWidget(segment_head)
        self.setLayout(self.layout)

        # Floating drag handle, not part of the layout
        self.drag_handle = DragHandle(self)
        self.drag_handle.setFixedSize(18, 18)
        self.drag_handle.setParent(self)  # child of container, but outside its layout
        self.drag_handle.move(4, 4)
        self.drag_handle.raise_()
        self.drag_handle.setVisible(False)

        # --- drag/drop for children INSIDE this container ---
        self.setAcceptDrops(True)
        self.active_drag_widget = None
        segment_head.set_drag_callback(self.set_active_drag_widget)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.drag_handle.move(4, 4)  # keep it pinned top-left on resize

    def set_container_drag_callback(self, callback):
        self.drag_handle.set_drag_callback(callback)

    def set_edit_mode(self, enabled: bool):
        self._edit_mode = enabled
        self.drag_handle.setVisible(enabled)
        if not enabled:
            self.recreate_segment()

    def recreate_segment(self):
        head = SegmentCombined(None, 0)
        head.clone_segment(self.segment_boxes[0].segment)
        self.segment = head
        for segment in self.segment_boxes[1:]:
            seg = SegmentCombined(None, 0)
            seg.clone_segment(segment.segment)
            head.set_next_segment(seg)
            head = seg
        head.set_next_segment(None)

        

    def addChild(self, segment):
        self.segment_boxes.append(segment)
        self.layout.addWidget(segment)
        segment.set_drag_callback(self.set_active_drag_widget)  # route child drags here, not to PageContainer

    def set_active_drag_widget(self, widget):
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

        self.layout.removeWidget(dragged_box)
        self.layout.insertWidget(target_index, dragged_box)
        self.sync_children()

        event.acceptProposedAction()

    def _calculate_drop_index(self, drop_y):
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget_middle_y = widget.y() + (widget.height() // 2)
                if drop_y < widget_middle_y:
                    return i
        return self.layout.count()

    def sync_children(self):
        """Re-link the combined segment chain to match the new visual order inside this block."""
        ordered = []
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, SegmentBox):
                ordered.append(widget)

        self.segment_boxes = ordered[:]