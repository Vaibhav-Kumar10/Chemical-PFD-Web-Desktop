from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QMdiArea

from src.canvas.widget import CanvasWidget
from src.component_library import ComponentLibrary
from src.theme import apply_theme_to_screen
from src.navigation import slide_to_index
import src.app_state as app_state

class CanvasScreen(QMainWindow):
    def __init__(self):
        super().__init__()

        from src.menubar import MenuBarManager
        self.menu_manager = MenuBarManager(self)
        self._connect_menu_signals()

        container = QWidget()
        self.setCentralWidget(container)
        
        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.library = ComponentLibrary(self)
        self.library.setMinimumWidth(280)
        main_layout.addWidget(self.library)

        self.mdi_area = QtWidgets.QMdiArea()
        self.mdi_area.setViewMode(QtWidgets.QMdiArea.TabbedView)
        self.mdi_area.setTabsClosable(True)
        self.mdi_area.setTabsMovable(True)
        self.mdi_area.setBackground(QBrush(QColor("#505050")))
        
        main_layout.addWidget(self.mdi_area)

        apply_theme_to_screen(self)

    def _connect_menu_signals(self):
        self.menu_manager.new_project_clicked.connect(self.on_new_project)
        self.menu_manager.back_home_clicked.connect(self.on_back_home)
        self.menu_manager.delete_clicked.connect(self.on_delete_component)
        self.menu_manager.logout_clicked.connect(self.logout)

        # Placeholders
        self.menu_manager.open_project_clicked.connect(lambda: print("Open Project clicked"))
        self.menu_manager.save_project_clicked.connect(lambda: print("Save Project clicked"))
        self.menu_manager.generate_image_clicked.connect(lambda: print("Generate Image clicked"))
        self.menu_manager.generate_report_clicked.connect(lambda: print("Generate Report clicked"))
        self.menu_manager.add_symbols_clicked.connect(lambda: print("Add Symbols clicked"))

    def on_new_project(self):
        canvas = CanvasWidget(self)
        canvas.update_canvas_theme()
        
        sub = self.mdi_area.addSubWindow(canvas)
        sub.setWindowTitle("New Project")
        sub.showMaximized()

    def on_back_home(self):
        slide_to_index(3, direction=-1)

    def on_delete_component(self):
        active_sub = self.mdi_area.currentSubWindow()
        if active_sub and isinstance(active_sub.widget(), CanvasWidget):
            active_sub.widget().delete_selected_components()

    def logout(self):
        app_state.access_token = None
        app_state.refresh_token = None
        app_state.current_user = None
        slide_to_index(0, direction=-1)
