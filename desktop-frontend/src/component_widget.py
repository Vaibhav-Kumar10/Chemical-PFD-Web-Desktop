import os
from PyQt5.QtWidgets import QWidget
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import Qt, QRectF, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen

class ComponentWidget(QWidget):
    def __init__(self, svg_path, parent=None, config=None):
        super().__init__(parent)
        self.svg_path = svg_path
        self.config = config or {}

        # SVG renderer
        self.renderer = QSvgRenderer(svg_path)

        # Fixed size (matches your canvas layout)
        self.setFixedSize(100, 80)

        # Selection + Hover
        self.hover_port = None
        self.is_selected = False

        self.setAttribute(Qt.WA_Hover, True)
        self.setMouseTracking(True)

        # Drag state
        self.drag_start_global = None

    # ----------------------------------------------------
    # CONTENT RECT (SVG + ports region)
    # ----------------------------------------------------
    def get_content_rect(self):
        bottom_pad = 25 if self.config.get('default_label') else 10
        w = max(1, self.width() - 20)
        h = max(1, self.height() - 10 - bottom_pad)
        return QRectF(10, 10, w, h)

    # ----------------------------------------------------
    # PAINT
    # ----------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 1. Draw selection outline
        if self.is_selected:
            painter.setPen(QPen(QColor("#60a5fa"), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 8, 8)

        # 2. Draw SVG
        content_rect = self.get_content_rect()
        self.renderer.render(painter, content_rect)

        # 3. Draw default label
        if self.config.get("default_label"):
            painter.setPen(QPen(Qt.black))
            label_rect = QRectF(0, content_rect.bottom() + 2, self.width(), 20)
            painter.drawText(label_rect, Qt.AlignCenter, self.config["default_label"])

        # 4. Draw ports
        grips = self.config.get("grips")
        if not grips:
            grips = [
                {"x": 0, "y": 50, "side": "left"},
                {"x": 100, "y": 50, "side": "right"},
            ]

        for idx, grip in enumerate(grips):
            self.draw_port(painter, grip, idx, content_rect)

    # ----------------------------------------------------
    # DRAW PORT
    # ----------------------------------------------------
    def draw_port(self, painter, grip, idx, content_rect):
        cx = content_rect.x() + (grip["x"] / 100.0) * content_rect.width()
        cy = content_rect.y() + (grip["y"] / 100.0) * content_rect.height()
        center = QPoint(int(cx), int(cy))

        radius = 6 if self.hover_port == idx else 4
        color = QColor("#22c55e") if self.hover_port == idx else QColor("cyan")

        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, radius, radius)

    # ----------------------------------------------------
    # SET SELECTED
    # ----------------------------------------------------
    def set_selected(self, selected):
        self.is_selected = selected
        self.update()

    # ----------------------------------------------------
    # SELECTION + START DRAG
    # ----------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            ctrl = bool(event.modifiers() & Qt.ControlModifier)

            if hasattr(self.parent(), "handle_selection"):
                self.parent().handle_selection(self, ctrl)
            else:
                self.is_selected = True
                self.update()

            self.drag_start_global = event.globalPos()
            event.accept()
        else:
            super().mousePressEvent(event)

    # ----------------------------------------------------
    # HOVER + DRAG MOVE
    # ----------------------------------------------------
    def mouseMoveEvent(self, event):
        pos = event.pos()

        grips = self.config.get("grips") or [
            {"x": 0, "y": 50, "side": "left"},
            {"x": 100, "y": 50, "side": "right"},
        ]

        content_rect = self.get_content_rect()

        prev_hover = self.hover_port
        self.hover_port = None

        # Hover detection
        for idx, g in enumerate(grips):
            cx = content_rect.x() + (g["x"] / 100.0) * content_rect.width()
            cy = content_rect.y() + (g["y"] / 100.0) * content_rect.height()
            center = QPoint(int(cx), int(cy))

            if (pos - center).manhattanLength() < 10:
                self.hover_port = idx
                break

        if prev_hover != self.hover_port:
            self.update()

        # Dragging movement
        if event.buttons() & Qt.LeftButton and self.drag_start_global:
            delta = event.globalPos() - self.drag_start_global
            parent = self.parent()

            if parent and hasattr(parent, "components"):
                for comp in parent.components:
                    if comp.is_selected:
                        comp.move(comp.pos() + delta)
            else:
                self.move(self.pos() + delta)

            self.drag_start_global = event.globalPos()

    # ----------------------------------------------------
    # STOP DRAG
    # ----------------------------------------------------
    def mouseReleaseEvent(self, event):
        self.drag_start_global = None
        super().mouseReleaseEvent(event)
