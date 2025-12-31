from PyQt5 import QtWidgets
import src.app_state as app_state

from src.fader import ThemeFader

def apply_theme_to_screen(screen, theme=None):
    """Apply theme to one screen by setting bgwidget[theme] property.
    Used by screens when they receive theme_changed signal from theme manager.
    """
    if theme is None:
        theme = app_state.current_theme
    else:
        app_state.current_theme = theme

    bg = screen.findChild(QtWidgets.QWidget, "bgwidget")
    if bg is not None:
        bg.setProperty("theme", theme)
        bg.style().unpolish(bg)
        bg.style().polish(bg)
        
        # Force update on all children to ensure inherited styles (like [theme="dark"] descendant selectors) apply
        for child in bg.findChildren(QtWidgets.QWidget):
            child.style().unpolish(child)
            child.style().polish(child)
        
        bg.update()
