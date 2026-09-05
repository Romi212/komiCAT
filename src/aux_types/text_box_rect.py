from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsItem
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QCursor
from PyQt6.QtCore import Qt, QRectF

class textBoxRect(QGraphicsRectItem):
    STYLES = {
        "text_bubble": {"bg": QColor(200, 0, 0, 50), "border": QColor(255, 0, 0)},
        "free_text":   {"bg": QColor(0, 0, 200, 50), "border": QColor(0, 0, 255)},
        "other":       {"bg": QColor(0, 200, 0, 50), "border": QColor(0, 255, 0)},
    }

    def __init__(self, text_box, parent = None, width=80, height=30, alpha=0.6):
        w = text_box.xmax - text_box.xmin
        h = text_box.ymax - text_box.ymin
        super().__init__(0, 0, w, h, parent)

        self.segment = None
        self.text_box = text_box
        self.text = ""
        self.number = 0

        self.state = "not_extracted" # not_extracted, extracted, focused

        self.style_config = self.STYLES.get(text_box.label, self.STYLES["other"])

        # Native QGraphicsItem flags replace manual proxy dragging logic
        self.setPos(text_box.xmin, text_box.ymin)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)
        self._resize_edge = None        

    def _get_hit_zone(self, pos):
        """Hit test for 8-direction resize handles."""
        m = 8  # handle margin
        r = self.rect()
        x, y = pos.x(), pos.y()

        left, right = x < m, x > r.width() - m
        top, bottom = y < m, y > r.height() - m

        if top and left: return "TL"
        if top and right: return "TR"
        if bottom and left: return "BL"
        if bottom and right: return "BR"
        if left: return "L"
        if right: return "R"
        if top: return "T"
        if bottom: return "B"
        return "MOVE"

    def _update_cursor(self, zone: str):
        cursors = {
            "TL": Qt.CursorShape.SizeFDiagCursor,
            "BR": Qt.CursorShape.SizeFDiagCursor,
            "TR": Qt.CursorShape.SizeBDiagCursor,
            "BL": Qt.CursorShape.SizeBDiagCursor,
            "L": Qt.CursorShape.SizeHorCursor,
            "R": Qt.CursorShape.SizeHorCursor,
            "T": Qt.CursorShape.SizeVerCursor,
            "B": Qt.CursorShape.SizeVerCursor,
            "MOVE": Qt.CursorShape.SizeAllCursor if self.state == "not_extracted" else Qt.CursorShape.ArrowCursor
        }
        self.setCursor(cursors.get(zone, Qt.CursorShape.ArrowCursor))

    def hoverMoveEvent(self, event):
        if self.state == "not_extracted":
            zone = self._get_hit_zone(event.pos())
            self._update_cursor(zone)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.state == "not_extracted":
            self._is_dragging = True
            self._has_moved = False
            self._drag_start_scene = event.scenePos()
            self._start_pos = self.pos()
            self._start_rect = self.rect()
            self._hit_zone = self._get_hit_zone(event.pos())
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):

        if self._is_dragging:
            delta = event.scenePos() - self._drag_start_scene

            if delta.manhattanLength() > 3:
                self._has_moved = True

            if self._hit_zone == "MOVE":
                new_pos = self._start_pos + delta
                self.setPos(new_pos)
            else:
                start_w, start_h = self._start_rect.width(), self._start_rect.height()
                start_x, start_y = self._start_pos.x(), self._start_pos.y()
                min_s = 20.0

                new_w, new_h = start_w, start_h
                new_x, new_y = start_x, start_y

                if "R" in self._hit_zone:
                    new_w = max(min_s, start_w + delta.x())
                elif "L" in self._hit_zone:
                    possible_w = start_w - delta.x()
                    if possible_w >= min_s:
                        new_w = possible_w
                        new_x = start_x + delta.x()
                    else:
                        new_w = min_s
                        new_x = start_x + (start_w - min_s)

                if "B" in self._hit_zone:
                    new_h = max(min_s, start_h + delta.y())
                elif "T" in self._hit_zone:
                    possible_h = start_h - delta.y()
                    if possible_h >= min_s:
                        new_h = possible_h
                        new_y = start_y + delta.y()
                    else:
                        new_h = min_s
                        new_y = start_y + (start_h - min_s)

                self.prepareGeometryChange()
                self.setPos(new_x, new_y)
                self.setRect(0, 0, new_w, new_h)

            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._resize_edge = None
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        super().mouseReleaseEvent(event)

    def paint(self, painter, option, widget=None):
        """Replaces QSS completely with fast, native vector painting."""
        rect = self.rect()

        if self.state == "extracted":
            pen = QPen(QColor("gray"), 1, Qt.PenStyle.SolidLine)
            brush = QBrush(QColor(0, 0, 0, 0))
        elif self.state == "focused":
            pen = QPen(QColor("blue"), 4, Qt.PenStyle.SolidLine)
            brush = QBrush(QColor(0, 0, 0, 0))
        else:
            border_width = 6 if self.isSelected() else 2
            pen = QPen(self.style_config["border"], border_width)
            brush = QBrush(self.style_config["bg"])

        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRoundedRect(rect, 4, 4)

        # Draw selection number text
        if self.number > 0 and self.state == "not_extracted":
            painter.setPen(QPen(QColor("white")))
            painter.setFont(QFont("Arial", int(min(rect.height() * 0.5, 36)), QFont.Weight.Bold))
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(self.number))