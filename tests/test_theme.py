"""
Tests for theme.py — color/palette definitions.

Constructing a QPalette needs a QApplication instance to be safe across
platforms, so this file runs headless via Qt's offscreen platform plugin
when no display is available (harmless when a real display is present
too - it only sets the env var if unset, respecting the developer's own
setup on their desktop machine).
"""

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest  # noqa: E402
from PyQt6.QtGui import QColor, QPalette  # noqa: E402
from PyQt6.QtWidgets import QApplication  # noqa: E402

from theme import (  # noqa: E402
    DARK_COLORS,
    LIGHT_COLORS,
    apply_theme,
    get_colors,
    get_palette,
)


@pytest.fixture(scope="module")
def app():
    instance = QApplication.instance()
    if instance is None:
        instance = QApplication(sys.argv)
    return instance


# ----------------------------------------------------------------------
# get_colors
# ----------------------------------------------------------------------

def test_get_colors_dark_matches_constant():
    assert get_colors(True) == DARK_COLORS


def test_get_colors_light_matches_constant():
    assert get_colors(False) == LIGHT_COLORS


def test_get_colors_returns_a_copy_not_the_original_dict():
    colors = get_colors(True)
    colors["window"] = "#000000"
    assert DARK_COLORS["window"] != "#000000"


# ----------------------------------------------------------------------
# get_palette
# ----------------------------------------------------------------------

def test_get_palette_dark_window_color(app):
    palette = get_palette(True)
    assert palette.color(QPalette.ColorRole.Window) == QColor(DARK_COLORS["window"])


def test_get_palette_light_window_color(app):
    palette = get_palette(False)
    assert palette.color(QPalette.ColorRole.Window) == QColor(LIGHT_COLORS["window"])


def test_get_palette_text_entry_colors(app):
    dark_palette = get_palette(True)
    assert dark_palette.color(QPalette.ColorRole.Base) == QColor(DARK_COLORS["base"])
    assert dark_palette.color(QPalette.ColorRole.Text) == QColor(DARK_COLORS["text"])


def test_get_palette_button_colors(app):
    light_palette = get_palette(False)
    assert light_palette.color(QPalette.ColorRole.Button) == QColor(LIGHT_COLORS["button"])
    assert light_palette.color(QPalette.ColorRole.ButtonText) == QColor(
        LIGHT_COLORS["button_text"]
    )


def test_get_palette_disabled_text_is_legible_placeholder_color(app):
    dark_palette = get_palette(True)
    disabled_text = dark_palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text)
    assert disabled_text == QColor(DARK_COLORS["placeholder_text"])


# ----------------------------------------------------------------------
# apply_theme
# ----------------------------------------------------------------------

def test_apply_theme_sets_fusion_style(app):
    apply_theme(app, dark_mode=True)
    assert app.style().objectName().lower() == "fusion"


def test_apply_theme_installs_dark_palette(app):
    apply_theme(app, dark_mode=True)
    assert app.palette().color(QPalette.ColorRole.Window) == QColor(DARK_COLORS["window"])


def test_apply_theme_installs_light_palette(app):
    apply_theme(app, dark_mode=False)
    assert app.palette().color(QPalette.ColorRole.Window) == QColor(LIGHT_COLORS["window"])
