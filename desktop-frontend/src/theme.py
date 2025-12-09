from PyQt5 import QtWidgets
import src.app_state as app_state

def apply_theme_to_screen(screen, theme=None):
    """Apply theme to one screen by setting bgwidget[theme] property."""
    if theme is None:
        theme = app_state.current_theme
    else:
        app_state.current_theme = theme

    bg = screen.findChild(QtWidgets.QWidget, "bgwidget")
    if bg is not None:
        bg.setProperty("theme", theme)
        bg.style().unpolish(bg)
        bg.style().polish(bg)
        bg.update()


def apply_theme_to_all(theme):
    """Apply theme to all pages in the stacked widget."""
    app_state.current_theme = theme
    if app_state.widget is None:
        return
    for i in range(app_state.widget.count()):
        s = app_state.widget.widget(i)
        apply_theme_to_screen(s, theme)
