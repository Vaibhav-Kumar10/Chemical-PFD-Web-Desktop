"""
Centralized theme management system that keeps all screens in sync.
"""

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette
import src.app_state as app_state


class ThemeManager(QObject):
    """
    Singleton theme manager that coordinates theme changes across all screens.
    """
    theme_changed = pyqtSignal(str)  # Emits "light" or "dark"
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        super().__init__()
        self._initialized = True
        self.manual_override = False
        
        # Detect initial system theme
        self.current_theme = self._detect_system_theme()
        app_state.current_theme = self.current_theme
        
        print(f"[THEME MANAGER] Initialized with theme: {self.current_theme}")
    
    def _detect_system_theme(self):
        """Detect if system is in dark mode."""
        palette = QApplication.palette()
        text_lightness = palette.color(QPalette.WindowText).lightness()
        bg_lightness = palette.color(QPalette.Window).lightness()
        return "dark" if text_lightness > bg_lightness else "light"
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.manual_override = True
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.set_theme(new_theme)
    
    def set_theme(self, theme):
        """Set a specific theme and notify all listeners."""
        if theme not in ["light", "dark"]:
            return
            
        self.current_theme = theme
        app_state.current_theme = theme
        
        print(f"[THEME MANAGER] Theme changed to: {theme}")
        self.theme_changed.emit(theme)
    
    def on_system_theme_changed(self):
        """Called when system theme changes (detected via changeEvent)."""
        if self.manual_override:
            # User has manually set a theme, don't auto-switch
            return
            
        detected_theme = self._detect_system_theme()
        if detected_theme != self.current_theme:
            self.set_theme(detected_theme)


# Global singleton instance
theme_manager = ThemeManager()