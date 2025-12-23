import os
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QPoint, QPointF
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QPainter

from src.component_widget import ComponentWidget
import src.app_state as app_state
from src.canvas import resources, painter

class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Canvas background
        self.setObjectName("canvasArea")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(palette)

        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

        # State
        self.components = []
        self.connections = []
        self.active_connection = None

        # Configs
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.component_config = resources.load_config(base_dir)
        self.label_data = resources.load_label_data(base_dir)
        self.base_dir = base_dir # store for svg finding

    def update_canvas_theme(self):
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(palette)
        self.update()

    # ---------------------- DRAG & DROP ----------------------
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        pos = event.pos()
        text = event.mimeData().text()
        self.add_component_label(text, pos)
        event.acceptProposedAction()

    def deselect_all(self):
        for comp in self.components:
            comp.set_selected(False)
        
        # Deselect connections (check existence just in case)
        for conn in self.connections:
            conn.is_selected = False

        self.update()

    # ---------------------- SELECTION + CONNECTION LOGIC ----------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.deselect_all()

            # Connection hit test
            hit_connection = None
            hit_index = -1
            for conn in self.connections:
                idx = conn.hit_test(event.pos())
                if idx != -1:
                    hit_connection = conn
                    hit_index = idx
                    break

            if hit_connection:
                # Drag logic for connection
                hit_connection.is_selected = True
                self.drag_connection = hit_connection
                self.drag_start_pos = event.pos()

                # Determine best sensitivity param (simplified logic from original)
                best_param = "path_offset"
                best_sensitivity = QPointF(0, 0)
                best_mag_sq = -1

                params = ["path_offset", "start_adjust", "end_adjust"]
                base_points = list(hit_connection.path)

                # Heuristic to find which parameter moves the segment under cursor
                for p in params:
                    old = getattr(hit_connection, p)
                    setattr(hit_connection, p, old + 1.0)
                    hit_connection.calculate_path()
                    new_points = hit_connection.path
                    
                    sens = QPointF(0, 0)
                    if hit_index < len(base_points) - 1 and hit_index < len(new_points) - 1:
                        a = (base_points[hit_index] + base_points[hit_index + 1]) / 2
                        b = (new_points[hit_index] + new_points[hit_index + 1]) / 2
                        sens = b - a
                    
                    setattr(hit_connection, p, old)
                    mag = sens.x()**2 + sens.y()**2
                    if mag > best_mag_sq:
                        best_mag_sq = mag
                        best_param = p
                        best_sensitivity = sens
                
                hit_connection.path = list(base_points)
                hit_connection.calculate_path()

                self.drag_param_name = best_param
                self.drag_sensitivity = best_sensitivity
                self.drag_start_param_val = getattr(hit_connection, best_param)

                self.setFocus()
                self.update()
                event.accept()
                return

        # Clicked blank
        self.active_connection = None
        self.drag_connection = None
        self.setFocus()
        event.accept()

    def mouseMoveEvent(self, event):
        if self.active_connection:
            self.update_connection_drag(event.pos())
            return super().mouseMoveEvent(event)

        if hasattr(self, "drag_connection") and self.drag_connection:
            delta = event.pos() - self.drag_start_pos
            sens_sq = self.drag_sensitivity.x()**2 + self.drag_sensitivity.y()**2
            
            if sens_sq > 0.001:
                dot = delta.x() * self.drag_sensitivity.x() + delta.y() * self.drag_sensitivity.y()
                change = dot / sens_sq
                new_val = self.drag_start_param_val + change
                setattr(self.drag_connection, self.drag_param_name, new_val)
                self.drag_connection.calculate_path()
                self.update()

        super().mouseMoveEvent(event)

    def update_connection_drag(self, pos):
        if not self.active_connection:
            return

        snap = False
        for comp in self.components:
            # Simple bounds check
            if not comp.geometry().adjusted(-30, -30, 30, 30).contains(pos):
                continue
            
            grips = comp.config.get("grips") or [
                {"x": 0, "y": 50, "side": "left"},
                {"x": 100, "y": 50, "side": "right"}
            ]
            content = comp.get_content_rect()

            for i, g in enumerate(grips):
                cx = content.x() + (g["x"] / 100) * content.width()
                cy = content.y() + (g["y"] / 100) * content.height()
                center = comp.mapToParent(QPoint(int(cx), int(cy)))

                if (pos - center).manhattanLength() < 20 and comp != self.active_connection.start_component:
                    self.active_connection.set_snap_target(comp, i, g["side"])
                    snap = True
                    break
            if snap: 
                break

        if not snap:
            self.active_connection.clear_snap_target()
            self.active_connection.current_pos = pos

        self.active_connection.calculate_path(self.components)
        self.update()

    def mouseReleaseEvent(self, event):
        self.handle_connection_release(event.pos())
        self.drag_connection = None
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            self.delete_selected_components()
        else:
            super().keyPressEvent(event)

    def delete_selected_components(self):
        to_del_comps = [c for c in self.components if c.is_selected]
        to_del_conns = [c for c in self.connections if c.is_selected]

        for i in range(len(self.connections) - 1, -1, -1):
            conn = self.connections[i]
            if (conn.start_component in to_del_comps or 
                conn.end_component in to_del_comps or 
                conn in to_del_conns):
                self.connections.pop(i)

        for comp in to_del_comps:
            if comp in self.components:
                self.components.remove(comp)
            comp.deleteLater()
        
        self.update()

    def handle_connection_release(self, pos):
        if self.active_connection:
            if self.active_connection.snap_component:
                self.active_connection.set_end_grip(
                    self.active_connection.snap_component,
                    self.active_connection.snap_grip_index,
                    self.active_connection.snap_side
                )
                self.active_connection.calculate_path(self.components)
                self.connections.append(self.active_connection)
            
            self.active_connection = None
            self.update()

    # ---------------------- PAINT EVENT ----------------------
    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        
        painter.draw_grid(qp, self.width(), self.height(), app_state.current_theme)
        painter.draw_connections(qp, self.connections, self.components)
        painter.draw_active_connection(qp, self.active_connection)

    # ---------------------- COMPONENT CREATION ----------------------
    def add_component_label(self, text, pos):
        # Use separated logic
        svg = resources.find_svg_path(text, self.base_dir)
        config = resources.get_component_config_by_name(text, self.component_config) or {}

        # Label generation
        key = resources.clean_string(text)
        label_text = text

        if key in self.label_data:
            d = self.label_data[key]
            d["count"] += 1
            label_text = f"{d['legend']}{d['count']:02d}{d['suffix']}"

        config["default_label"] = label_text

        if not svg:
            lbl = QLabel(label_text, self)
            lbl.move(pos)
            lbl.setStyleSheet("color:white; background:rgba(0,0,0,0.5); padding:4px; border-radius:4px;")
            lbl.show()
            lbl.adjustSize()
            return

        comp = ComponentWidget(svg, self, config=config)
        comp.move(pos)
        comp.show()
        self.components.append(comp)
