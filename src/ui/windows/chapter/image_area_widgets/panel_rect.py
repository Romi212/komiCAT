from PyQt6.QtWidgets import QGraphicsRectItem
from PyQt6.QtGui import QPen, QBrush, QColor, QFont, QPainter
from PyQt6.QtCore import Qt, QRectF
from ui import theme


class PanelFrame(QGraphicsRectItem):
    """Decorative frame around a detected manga panel (not interactive)."""

    BORDER = 4
    LABEL_H = 26
    LABEL_PAD = 10

    def __init__(self, x, y, w, h, label):
        super().__init__(0, 0, w, h)
        self.setPos(x, y)
        self.label = label
        self.setZValue(-1)                                   # below bubble boxes
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)  # clicks pass through to the boxes

    def boundingRect(self):
        return self.rect().adjusted(-self.BORDER, -self.BORDER, self.BORDER, self.BORDER)

    def paint(self, painter, option, widget=None):
        t = theme.current()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # ---- frame ----
        pen = QPen(QColor(t.panel_border), self.BORDER)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        half = self.BORDER / 2
        rect = self.rect()
        painter.drawRoundedRect(rect.adjusted(half, half, -half, -half), 6, 6)

        # ---- label pill, top-left, sitting on the border ----
        font = QFont("Arial")
        font.setBold(True)
        font.setPixelSize(int(self.LABEL_H * 0.6))
        painter.setFont(font)
        text_w = painter.fontMetrics().horizontalAdvance(self.label)
        pill = QRectF(half, half, text_w + 2 * self.LABEL_PAD, self.LABEL_H)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(t.panel_label_bg))
        painter.drawRoundedRect(pill, 6, 6)
        painter.setPen(QColor(t.badge_text))
        painter.drawText(pill, Qt.AlignmentFlag.AlignCenter, self.label)