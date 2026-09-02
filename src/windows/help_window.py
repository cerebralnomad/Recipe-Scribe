"""
windows/help_window.py

Modal dialog showing the program's usage instructions.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtWidgets import QDialog, QPushButton, QTextEdit, QVBoxLayout, QWidget

from resources.help_text import HELP_TEXT


class HelpWindow(QDialog):
    """Read-only scrollable help text with a Close button."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Program Usage")
        self.resize(700, 600)

        layout = QVBoxLayout(self)

        self.text_box = QTextEdit()
        self.text_box.setPlainText(HELP_TEXT)
        self.text_box.setReadOnly(True)
        layout.addWidget(self.text_box)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
