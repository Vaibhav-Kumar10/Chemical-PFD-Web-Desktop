import os
import csv
import requests
import src.app_state as app_state
from src import api_client
from PyQt5.QtCore import Qt, QMimeData, QSize
from PyQt5.QtGui import QIcon, QDrag, QMovie
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, 
    QScrollArea, QLabel, QToolButton, QGridLayout, QLabel, QApplication
)
from PyQt5.QtCore import QEvent

class FunctionEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, fn):
        super().__init__(FunctionEvent.EVENT_TYPE)
        self.fn = fn

    def execute(self):
        self.fn()


class ComponentButton(QToolButton):
    def __init__(self, component_data, icon_path, parent=None):
        super().__init__(parent)
        self.component_data = component_data
        
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(42, 42))
        
        self.setToolTip(component_data['name'])
        self.setFixedSize(56, 56)
        self.setStyleSheet("""
            QToolButton {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                padding: 2px;
            }
            QToolButton:hover {
                border: 2px solid #0078d7;
                background-color: #e5f3ff;
            }
        """)
        
        self.dragStartPosition = None
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.dragStartPosition = event.pos()
    
    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if not self.dragStartPosition:
            return
        if (event.pos() - self.dragStartPosition).manhattanLength() < 10:
            return
        
        drag = QDrag(self)
        mimeData = QMimeData()
        mimeData.setText(self.component_data['object'])
        drag.setMimeData(mimeData)
        
        if not self.icon().isNull():
            drag.setPixmap(self.icon().pixmap(32, 32))
        
        drag.exec_(Qt.CopyAction)


class ComponentLibrary(QWidget):
    def __init__(self, parent=None):
        super(ComponentLibrary, self).__init__(parent)
        
        self.setMinimumWidth(260)
        self.setMaximumWidth(260)
        
        self.component_data = []
        self.icon_buttons = []
        self.category_widgets = []
        
        self._setup_ui()
        self._sync_components_with_backend()
        self._load_components()
        self._populate_icons()

        # Loader animation (hidden by default)
        self.loader_label = QLabel(self)
        self.loader_label.setAlignment(Qt.AlignCenter)
        self.loader_label.setStyleSheet("background: transparent;")
        self.loader_movie = QMovie("ui/assets/loading.gif")  # put gif in assets
        self.loader_label.setMovie(self.loader_movie)
        self.loader_label.setVisible(False)

    
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        title = QLabel("Components")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #333; margin-bottom: 5px;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search components...")
        self.search_box.textChanged.connect(self._filter_icons)
        main_layout.addWidget(self.search_box)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scroll_layout.setSpacing(10)
        
        self.scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll_area)
        
    def _show_loader(self):
        # Center the loader overlay
        size = 80  # overlay size
        self.loader_label.setGeometry(
            (self.width() - size) // 2,
            (self.height() - size) // 2,
            size, size
        )
        self.loader_label.setVisible(True)
        self.loader_movie.start()
        self.loader_label.raise_()

        QApplication.processEvents()

    def _hide_loader(self):
        self.loader_movie.stop()
        self.loader_label.setVisible(False)

    def _load_components(self):
        csv_path = os.path.join("ui", "assets", "Component_Details.csv")
        
        if not os.path.exists(csv_path):
            return
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['parent'] and row['name']:
                        self.component_data.append({
                            "s_no": row.get("s_no", "").strip(),
                            "parent": row.get("parent", "").strip(),
                            "name": row.get("name", "").strip(),
                            "legend": row.get("legend", "").strip(),
                            "suffix": row.get("suffix", "").strip(),
                            "object": row.get("object", "").strip(),
                            "svg": row.get("svg", "").strip(),
                            "png": row.get("png", "").strip(),
                            "grips": row.get("grips", "").strip()
                        })
        except Exception as e:
            print(f"Error loading components: {e}")

    def _sync_components_with_backend(self):
        """
        Fetch components from backend, append new ones to CSV,
        and download PNG/SVG exactly as backend provides.
        """
        try:
            api_components = api_client.get_components()
            if not api_components:
                return

            csv_path = os.path.join("ui", "assets", "Component_Details.csv")

            # Get existing S. No list
            existing = set()
            if os.path.exists(csv_path):
                with open(csv_path, "r", encoding="utf-8-sig") as f:
                    for r in csv.DictReader(f):
                        if r.get("s_no"):
                            existing.add(r["s_no"].strip())

            new_rows = []

            for comp in api_components:

                s_no = str(comp.get("s_no", "")).strip()
                if not s_no or s_no in existing:
                    continue

                parent = comp.get("parent", "").strip()
                name = comp.get("name", "").strip()
                obj = comp.get("object", "").strip()

                png_url = comp.get("png_url") or comp.get("png")
                svg_url = comp.get("svg_url") or comp.get("svg")

                # Prepare folders
                parent_folder = self.FOLDER_MAP.get(parent, parent)
                png_dir = os.path.join("ui", "assets", "png", parent_folder)
                svg_dir = os.path.join("ui", "assets", "svg", parent_folder)
                os.makedirs(png_dir, exist_ok=True)
                os.makedirs(svg_dir, exist_ok=True)

                png_filename = ""
                svg_filename = ""

                # --- Download PNG ---
                if png_url:
                    if not png_url.startswith("http"):
                        png_url = f"{app_state.BACKEND_BASE_URL}{png_url}"

                    png_filename = os.path.basename(png_url)
                    png_path = os.path.join(png_dir, png_filename)

                    try:
                        res = requests.get(png_url, timeout=5)
                        if res.status_code == 200:
                            with open(png_path, "wb") as f:
                                f.write(res.content)
                            print(f"[SYNC] PNG saved → {png_path}")
                        else:
                            print("[SYNC] PNG download failed:", png_url)
                    except Exception as e:
                        print("[SYNC ERROR] PNG failed:", e)

                # --- Download SVG ---
                if svg_url:
                    if not svg_url.startswith("http"):
                        svg_url = f"{app_state.BACKEND_BASE_URL}{svg_url}"

                    svg_filename = os.path.basename(svg_url)
                    svg_path = os.path.join(svg_dir, svg_filename)

                    try:
                        res = requests.get(svg_url, timeout=5)
                        if res.status_code == 200:
                            with open(svg_path, "wb") as f:
                                f.write(res.content)
                            print(f"[SYNC] SVG saved → {svg_path}")
                    except Exception as e:
                        print("[SYNC ERROR] SVG failed:", e)

                # CSV row with exact backend filenames
                new_rows.append({
                    "s_no": s_no,
                    "parent": parent,
                    "name": name,
                    "legend": comp.get("legend", ""),
                    "suffix": comp.get("suffix", ""),
                    "object": obj,
                    "svg": svg_filename,
                    "png": png_filename,
                    "grips": comp.get("grips", "")
                })

            # Append to CSV
            if new_rows:
                file_exists = os.path.exists(csv_path)

                with open(csv_path, "a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=[
                        "s_no", "parent", "name", "legend", "suffix",
                        "object", "svg", "png", "grips"
                    ])

                    if not file_exists:
                        writer.writeheader()

                    for r in new_rows:
                        writer.writerow(r)

                print(f"[SYNC] Added {len(new_rows)} new components.")

        except Exception as e:
            print("[SYNC CRITICAL ERROR]", e)


    def _populate_icons(self):
        for i in reversed(range(self.scroll_layout.count())):
            w = self.scroll_layout.itemAt(i).widget()
            if w:
                w.deleteLater()
        
        self.icon_buttons.clear()
        self.category_widgets.clear()
        
        grouped = {}
        seen_components = set()
        
        for component in self.component_data:
            parent = component['parent']
            name = component['name']
            
            unique_key = (parent, name, component.get('object', ''))
            
            if unique_key in seen_components:
                # If we've seen this exact combination, skip
                continue
            
            # Additional check: If name is "Filter" in "Fittings", only allow one
            if parent == "Fittings" and name == "Filter":
                filter_key = ("Fittings", "Filter")
                if filter_key in seen_components:
                    continue
                seen_components.add(filter_key)

            seen_components.add(unique_key)
            
            if parent not in grouped:
                grouped[parent] = []
            grouped[parent].append(component)
        
        for parent_name in sorted(grouped.keys()):
            category_label = QLabel(parent_name)
            category_label.setStyleSheet("""
                QLabel {
                    font-size: 8pt;
                    padding: 5px;
                    background-color: #f0f0f0;
                    border-radius: 3px;
                }
            """)
            
            grid_widget = QWidget()
            grid_layout = QGridLayout(grid_widget)
            grid_layout.setSpacing(5)
            grid_layout.setContentsMargins(5, 5, 5, 5)
            grid_layout.setAlignment(Qt.AlignLeft)
            
            row, col = 0, 0
            max_cols = 5
            category_buttons = []
            
            for component in sorted(grouped[parent_name], key=lambda x: x['name']):
                icon_path = self._get_icon_path(parent_name, component['name'], component.get('object', ''))
                
                if os.path.exists(icon_path):
                    button = ComponentButton(component, icon_path)
                    button.setProperty('category', parent_name)
                    button.setProperty('component_name', component['name'])
                    grid_layout.addWidget(button, row, col)
                    self.icon_buttons.append(button)
                    category_buttons.append(button)
                    
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
            
            if category_buttons:
                self.scroll_layout.addWidget(category_label)
                self.scroll_layout.addWidget(grid_widget)
                self.category_widgets.append({
                    'label': category_label,
                    'grid': grid_widget,
                    'buttons': category_buttons,
                    'name': parent_name
                })
    
    def event(self, e):
        if isinstance(e, FunctionEvent):
            e.execute()
            return True
        return super().event(e)

    # Mappings for icon path resolution
    FOLDER_MAP = {
        "Furnance and Boilers": "Furnaces and Boilers",
        "Storage Vessels/ Tanks": "Storage Vessels Tanks",
        "Size Reduction Equipments": "Size Reduction Equipements"
    }

    NAME_CORRECTIONS = {
        "/": ", ",  # "Reducer/Expander" → "Reducer, Expander"
        "Furnance": "Furnace",  # Fix CSV typo
        "Drier": "Dryer",  # British to American spelling
        "Oil, Gas": "Oil Gas",  # Remove comma from compound name
        "Centrifugal Pumps": "Centrifugal Pump",  # Singular
        "Ejector (vapour service)": "Ejector(Vapor Service)",  # Match exact case
        "Plates, Trays (For mass Transfer)": "Trays or plates",  # Process Vessels  
        "Separators for Liquids, Decanters": "Separators for Liquids, Decanter"  # Separators
    }

    PREFIXED_COMPONENTS = {
        'Exchanger905': "905Exchanger",
        'KettleReboiler907': "907Kettle Reboiler"
    }

    def _get_icon_path(self, parent, name, obj=''):
        """
        Returns local PNG path.
        If missing, auto-downloads from backend/media/components/<file>.
        """

        # 1) Find the CSV entry for this component
        csv_row = None
        for c in self.component_data:
            if c["parent"] == parent and c["name"] == name:
                csv_row = c
                break

        backend_png_filename = csv_row.get("png", "") if csv_row else ""

        # 2) Build local folder path
        folder = self.FOLDER_MAP.get(parent, parent)
        local_dir = os.path.join("ui", "assets", "png", folder)
        os.makedirs(local_dir, exist_ok=True)

        # 3) If backend provided a filename (new components)
        if backend_png_filename:
            local_path = os.path.join(local_dir, backend_png_filename)

            # If already saved locally → use it
            if os.path.exists(local_path):
                return local_path

            # Else → download automatically
            backend_url = f"{app_state.BACKEND_BASE_URL}/media/components/{backend_png_filename}"

            try:
                print(f"[IMG FETCH] {backend_url}")
                r = requests.get(backend_url, timeout=5)
                if r.status_code == 200:
                    with open(local_path, "wb") as f:
                        f.write(r.content)
                    print(f"[IMG FETCH] Saved → {local_path}")
                    return local_path
                else:
                    print("[IMG FETCH ERROR] Failed:", r.status_code)
            except Exception as e:
                print("[IMG FETCH ERROR]", e)

        # 4) Fallback: use old cleaned-name system (old CSV entries)
        clean_name = obj and self.PREFIXED_COMPONENTS.get(obj)
        if not clean_name:
            clean_name = name
            for old, new in self.NAME_CORRECTIONS.items():
                clean_name = clean_name.replace(old, new)

        fallback_path = os.path.join(local_dir, f"{clean_name}.png")

        return fallback_path if os.path.exists(fallback_path) else ""

    
    def _filter_icons(self, search_text):
        search_text = search_text.lower()
        
        if not search_text:
            for category in self.category_widgets:
                category['label'].setVisible(True)
                category['grid'].setVisible(True)
                for button in category['buttons']:
                    button.setVisible(True)
            return
        
        for category in self.category_widgets:
            has_match = False
            
            for button in category['buttons']:
                component = button.property('component_name').lower()
                category_name = button.property('category').lower()
                
                matches = search_text in component or search_text in category_name
                button.setVisible(matches)
                
                if matches:
                    has_match = True
            
            category['label'].setVisible(has_match)
            category['grid'].setVisible(has_match)

    def reload_components(self):
        """
        Async reload with loading animation
        """
        self._show_loader()

        def task():
            # Background thread work
            self.component_data.clear()
            self._sync_components_with_backend()
            self._load_components()

            # Update UI on main thread
            QApplication.instance().postEvent(
                self,
                FunctionEvent(lambda: (
                    self._populate_icons(),
                    self._hide_loader()
                ))
            )

        import threading
        threading.Thread(target=task, daemon=True).start()