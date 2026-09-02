#!/usr/bin/env python3
"""
main.py

Entry point for Recipe Scribe Qt. Sets up the QApplication, loads config,
applies the theme, sets the app/window icon, and launches the AppShell
(which hosts the recipe entry and search pages).
"""

import configparser
import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from config import AppConfig
from theme import apply_theme
from windows.app_shell import AppShell

# Fallback used outside a Flatpak sandbox (plain CLI dev runs), and as the
# production app ID once this replaces the Tkinter version on Flathub.
_DEFAULT_DESKTOP_ID = "com.cerebralnomad.recipescribe"


def _detect_desktop_file_name() -> str:
    """
    Returns the installed .desktop file's base name (no extension), so Qt
    can correctly associate the running window with its icon and other
    desktop metadata. Without this, some window managers/taskbars show a
    generic fallback icon instead of the app's real one, since they can't
    match the running process back to an installed .desktop entry.

    Every Flatpak sandbox has a /.flatpak-info file (ini format, an
    [Application] group with a "name" key giving the actual installed app
    ID) - reading it here means this works correctly whether installed as
    com.cerebralnomad.recipescribe (production) or
    com.cerebralnomad.recipescribe-qt (a local test build), with no
    source change needed between the two. Outside a sandbox, this falls
    back to the production ID, which is harmless in a plain CLI dev run
    since there's no installed .desktop file to match against anyway.
    """
    flatpak_info_path = "/.flatpak-info"
    if os.path.exists(flatpak_info_path):
        parser = configparser.ConfigParser()
        parser.read(flatpak_info_path)
        app_id = parser.get("Application", "name", fallback=None)
        if app_id:
            return app_id
    return _DEFAULT_DESKTOP_ID


def _load_app_icon(desktop_file_name: str) -> QIcon:
    """
    Loads the application icon: the installed Flatpak location first
    (matching whichever app ID is actually running - production or a
    local test build), falling back to the repo's icons/ folder for
    non-Flatpak development runs.
    """
    candidates = [
        f"/app/share/icons/hicolor/256x256/apps/{desktop_file_name}.png",
        os.path.join(os.path.dirname(__file__), "..", "icons", "rc_256.png"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return QIcon(path)
    return QIcon()


def main() -> int:
    app = QApplication(sys.argv)

    desktop_file_name = _detect_desktop_file_name()
    app.setDesktopFileName(desktop_file_name)
    app.setWindowIcon(_load_app_icon(desktop_file_name))

    config = AppConfig()
    config.load()

    # Theme must be applied before any windows/widgets are constructed -
    # see theme.py's module docstring. A change to dark_mode at runtime
    # (via the Config menu) triggers a full restart, matching the original
    # app's behavior, rather than attempting a live palette swap.
    apply_theme(app, config.dark_mode)

    shell = AppShell(config)
    if config.start_fullscreen:
        shell.showFullScreen()
    else:
        shell.resize(1000, 700)
        shell.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
