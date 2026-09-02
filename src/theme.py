"""
theme.py

Light and dark palette definitions for Recipe Scribe Qt.

Colors are carried over from the original Tkinter app's dark/light mode
values (see recipe_scribe-2.0.1.py's `background`, `entry_bg`, etc.
variables) so the visual identity stays familiar, translated here into a
QPalette rather than per-widget color configuration.

Applying a custom QPalette only reliably overrides every widget's colors
under Qt's "Fusion" style - native styles (Windows/GTK/macOS) often ignore
palette roles they don't use internally, which would leave some widgets
stuck in the OS's own light/dark colors regardless of what we set here.
apply_theme() sets the app style to Fusion for this reason; this is a
common, well-established pattern for PyQt apps that need consistent
custom theming across platforms.
"""

from __future__ import annotations

from typing import Dict

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

# Color values ported directly from the original Tkinter app's dark_mode
# and light_mode branches, given descriptive keys instead of the
# original's ad hoc variable names (background, entry_bg, button_bg, ...).
DARK_COLORS: Dict[str, str] = {
    "window": "#343232",
    "window_text": "#ffffff",
    "base": "#1e1e1e",  # entry / text-edit backgrounds
    "text": "#ffffff",  # entry / text-edit text
    "button": "#404040",
    "button_text": "#ffffff",
    "highlight": "#5d5c5c",
    "highlighted_text": "#ffffff",
    "alternate_base": "#464444",  # scrollbar trough / alternating rows
    "placeholder_text": "#858585",
}

LIGHT_COLORS: Dict[str, str] = {
    "window": "#d4d4d4",
    "window_text": "#000000",
    "base": "#f2f2f2",
    "text": "#000000",
    "button": "#c4c4c4",
    "button_text": "#000000",
    "highlight": "#bababa",
    "highlighted_text": "#000000",
    "alternate_base": "#cccccc",
    "placeholder_text": "#858585",
}


def get_colors(dark_mode: bool) -> Dict[str, str]:
    """
    Returns the flat color-role dict for the requested mode, as a copy so
    callers can't accidentally mutate the shared DARK_COLORS/LIGHT_COLORS
    constants.
    """
    return dict(DARK_COLORS if dark_mode else LIGHT_COLORS)


def get_palette(dark_mode: bool) -> QPalette:
    """
    Builds a QPalette for the requested mode, covering every color role
    Recipe Scribe Qt's widgets actually use: window/label backgrounds,
    text-entry backgrounds and text, buttons, selection highlighting,
    and tooltips.
    """
    colors = get_colors(dark_mode)
    palette = QPalette()

    window = QColor(colors["window"])
    window_text = QColor(colors["window_text"])
    base = QColor(colors["base"])
    text = QColor(colors["text"])
    button = QColor(colors["button"])
    button_text = QColor(colors["button_text"])
    highlight = QColor(colors["highlight"])
    highlighted_text = QColor(colors["highlighted_text"])
    alternate_base = QColor(colors["alternate_base"])
    placeholder = QColor(colors["placeholder_text"])

    palette.setColor(QPalette.ColorRole.Window, window)
    palette.setColor(QPalette.ColorRole.WindowText, window_text)
    palette.setColor(QPalette.ColorRole.Base, base)
    palette.setColor(QPalette.ColorRole.AlternateBase, alternate_base)
    palette.setColor(QPalette.ColorRole.Text, text)
    palette.setColor(QPalette.ColorRole.Button, button)
    palette.setColor(QPalette.ColorRole.ButtonText, button_text)
    palette.setColor(QPalette.ColorRole.Highlight, highlight)
    palette.setColor(QPalette.ColorRole.HighlightedText, highlighted_text)
    palette.setColor(QPalette.ColorRole.ToolTipBase, base)
    palette.setColor(QPalette.ColorRole.ToolTipText, text)

    # Keep disabled-widget text legible in both themes rather than falling
    # back to Qt's default gray-on-gray, which is especially hard to read
    # in dark mode.
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, placeholder)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, placeholder)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, placeholder)

    return palette


def apply_theme(app: QApplication, dark_mode: bool) -> None:
    """
    Applies the requested theme to the whole application: sets the Fusion
    style (required for a custom QPalette to be respected consistently
    across platforms - see module docstring) and installs the matching
    palette.

    Call this once at startup in main.py, using AppConfig.dark_mode.
    """
    app.setStyle("Fusion")
    app.setPalette(get_palette(dark_mode))
