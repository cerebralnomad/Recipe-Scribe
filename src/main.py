#!/usr/bin/env python3
"""
main.py

Entry point for Recipe Scribe Qt. Sets up the QApplication, loads config,
applies the theme, and launches the AppShell (which hosts the recipe
entry and search pages).
"""

import sys

from PyQt6.QtWidgets import QApplication

from config import AppConfig
from theme import apply_theme
from windows.app_shell import AppShell


def main() -> int:
    app = QApplication(sys.argv)

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
