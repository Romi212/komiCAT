# image_area_widgets/combine_arrow.py
import math

from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsItem, QGraphicsPathItem, QGraphicsPolygonItem, QGraphicsSimpleTextItem
from PyQt6.QtGui import QFont, QPainterPath, QPainterPathStroker, QPen, QBrush, QColor, QPolygonF
from PyQt6.QtCore import QPointF, Qt

ARROW_COLOR = QColor("#6e2130")  # same accent as CombinedContainer

class UnlinkButton(QGraphicsEllipseItem):
    """Small round ✕ button shown at the middle of a CombineArrow while hovered."""
    RADIUS = 11

    def __init__(self, arrow):
        r = self.RADIUS
        super().__init__(-r, -r, 2 * r, 2 * r, arrow)
        self.arrow = arrow

        # Keeps a constant on-screen size no matter how far the view is zoomed
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        self.setZValue(11)
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Uncombine these segments")
        self._set_hovered(False)

        label = QGraphicsSimpleTextItem("✕", self)
        label.setBrush(QBrush(QColor("white")))
        label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        br = label.boundingRect()
        label.setPos(-br.width() / 2, -br.height() / 2)

        self.hide()

    def _set_hovered(self, hovered):
        self.setBrush(QBrush(QColor("#8a2e40") if hovered else ARROW_COLOR))
        self.setPen(QPen(QColor("white"), 1.5))

    def hoverEnterEvent(self, event):
        self.arrow._cancel_hide()   # cursor moved from the arrow onto the button
        self._set_hovered(True)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self._set_hovered(False)
        self.arrow._schedule_hide()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.arrow.request_remove()
            event.accept()
        else:
            super().mousePressEvent(event)
            
class CombineArrow(QGraphicsPathItem):
    """Curved arrow from the parent segment's top-left corner to the child's top-left corner.

    Follows both bubbles automatically through their `signals.moved` signal.
    """

    HEAD_SIZE = 16
    CURVE_FACTOR = 0.3   # how far the curve bulges, relative to the arrow length
    MAX_BEND = 60        # cap on the bulge, in scene pixels
    CURVED = True        # set to False for a straight arrow

    def __init__(self, parent_seg, child_seg, on_remove=None):
        super().__init__()
        self.edit_mode = False
        self.parent_seg = parent_seg
        self.child_seg = child_seg
        self.on_remove = on_remove   # optional: called as on_remove(parent_seg, child_seg)

        self.setZValue(10)  # above the bubble rects
        self.setPen(QPen(ARROW_COLOR, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        self.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Right-click to separate these segments")

        # Arrowhead is a child item so it moves/gets removed together with the arrow
        self.head = QGraphicsPolygonItem(self)
        self.head.setBrush(QBrush(ARROW_COLOR))
        self.head.setPen(QPen(ARROW_COLOR))

        # Follow both bubbles when they are moved or resized
        if self.parent_seg.button:
            self.parent_seg.button.signals.moved.connect(self.update_geometry)
        if self.child_seg.button:
            self.child_seg.button.signals.moved.connect(self.update_geometry)

        self.update_geometry()

    # ---------- geometry ----------

    @staticmethod
    def _corner(seg):
        """Top-left corner of a segment's rect in scene coordinates."""
        btn = seg.button
        if btn:
            return btn.mapToScene(btn.rect().topLeft())
        return QPointF(seg.text_box.xmin, seg.text_box.ymin)

    def update_geometry(self):
        p1 = self._corner(self.parent_seg)
        p2 = self._corner(self.child_seg)

        path = QPainterPath(p1)

        if self.CURVED:
            # Control point: midpoint pushed sideways, perpendicular to the line p1 -> p2
            mid = (p1 + p2) / 2
            dx, dy = p2.x() - p1.x(), p2.y() - p1.y()
            length = math.hypot(dx, dy) or 1.0
            bend = min(self.MAX_BEND, length * self.CURVE_FACTOR)
            ctrl = QPointF(mid.x() - dy / length * bend,
                           mid.y() + dx / length * bend)
            path.quadTo(ctrl, p2)
            tail = ctrl  # the arrowhead points along the curve's final tangent (ctrl -> p2)
        else:
            path.lineTo(p2)
            tail = p1

        self.prepareGeometryChange()
        self.setPath(path)
        self._update_head(tail, p2)

    def _update_head(self, tail, tip):
        angle = math.atan2(tip.y() - tail.y(), tip.x() - tail.x())
        s = self.HEAD_SIZE
        left = QPointF(tip.x() - s * math.cos(angle - 0.4),
                       tip.y() - s * math.sin(angle - 0.4))
        right = QPointF(tip.x() - s * math.cos(angle + 0.4),
                        tip.y() - s * math.sin(angle + 0.4))
        self.head.setPolygon(QPolygonF([tip, left, right]))

    # ---------- interaction ----------

    def shape(self):
        """Wider hit area so the thin curve is easy to click."""
        stroker = QPainterPathStroker()
        stroker.setWidth(14)
        return stroker.createStroke(self.path())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton and self.on_remove:
            self.on_remove(self.parent_seg, self.child_seg)
            event.accept()
        else:
            super().mousePressEvent(event)

    # ---------- lifecycle ----------

    def detach(self):
        """Disconnect from the bubbles and leave the scene. Call this when the link is dropped."""
        for seg in (self.parent_seg, self.child_seg):
            if seg.button:
                try:
                    seg.button.signals.moved.disconnect(self.update_geometry)
                except (TypeError, RuntimeError):
                    pass  # already disconnected
        if self.scene():
            self.scene().removeItem(self)