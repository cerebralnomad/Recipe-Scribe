"""
windows/about_window.py

Modal dialog showing version and license information.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtWidgets import QDialog, QPushButton, QTextEdit, QVBoxLayout, QWidget

from resources.about_text import ABOUT_TEXT


class AboutWindow(QDialog):
    """Read-only about text with a Close button."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.resize(500, 450)

        layout = QVBoxLayout(self)

        self.text_box = QTextEdit()
        self.text_box.setPlainText(ABOUT_TEXT)
        self.text_box.setReadOnly(True)
        layout.addWidget(self.text_box)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
