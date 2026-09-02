"""
windows/config_dialogs.py

Config-menu dialogs.

Restart behavior mirrors the original Tkinter app exactly: three settings
(bullet points, filename formatting, dark mode) call
AppConfig.apply_and_restart() because they change something already
visible on screen, and the original app always restarted immediately for
these. The fourth toggle, start-fullscreen, only affects window sizing at
the next launch - the original never restarted for it either, just saved
the value and confirmed it takes effect next time. This version preserves
that same distinction.
"""

from __future__ import annotations

from typing import List, Optional

from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import AppConfig


# ----------------------------------------------------------------------
# Default save path
# ----------------------------------------------------------------------

def prompt_set_default_save_path(parent: QWidget, config: AppConfig) -> bool:
    """
    Opens a folder picker for the default save path.
    Returns True if the path was changed, False if the user cancelled.
    """
    path = QFileDialog.getExistingDirectory(
        parent, "Select Default Save Path", config.save_path or ""
    )
    if not path:
        return False
    config.save_path = path
    config.save()
    return True


# ----------------------------------------------------------------------
# Restart-on-change toggles: bullet points, filename formatting, dark mode
# ----------------------------------------------------------------------

def _prompt_restart_toggle(
    parent: QWidget,
    title: str,
    status_text: str,
    yes_label: str,
    no_label: str,
) -> Optional[bool]:
    """
    Shows a Yes/No/Cancel dialog warning that the program will restart.
    Returns the chosen boolean setting, or None if the user cancelled.
    """
    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setText(status_text)
    box.setInformativeText(
        "The program will restart immediately to apply this change - "
        "save any unsaved recipe first."
    )
    yes_button = box.addButton(yes_label, QMessageBox.ButtonRole.YesRole)
    box.addButton(no_label, QMessageBox.ButtonRole.NoRole)
    cancel_button = box.addButton(QMessageBox.StandardButton.Cancel)
    box.exec()

    clicked = box.clickedButton()
    if clicked is cancel_button:
        return None
    return clicked is yes_button


def prompt_use_bullet_points(parent: QWidget, config: AppConfig) -> None:
    current = "currently ON" if config.use_bullet_points else "currently OFF"
    choice = _prompt_restart_toggle(
        parent,
        "Bullet Point Configuration",
        f"Bullet points for ingredients are {current}.",
        "Use Bullet Points",
        "No Bullet Points",
    )
    if choice is None:
        return
    config.use_bullet_points = choice
    config.apply_and_restart()


def prompt_format_filename(parent: QWidget, config: AppConfig) -> None:
    current = "currently ON" if config.format_filename else "currently OFF"
    choice = _prompt_restart_toggle(
        parent,
        "Filename Formatting Configuration",
        f"Automatic filename formatting is {current}.",
        "Format Filenames",
        "Use Title As Typed",
    )
    if choice is None:
        return
    config.format_filename = choice
    config.apply_and_restart()


def prompt_dark_mode(parent: QWidget, config: AppConfig) -> None:
    current = "Dark Mode" if config.dark_mode else "Light Mode"
    choice = _prompt_restart_toggle(
        parent,
        "Theme Configuration",
        f"You are currently using {current}.",
        "Dark Mode",
        "Light Mode",
    )
    if choice is None:
        return
    config.dark_mode = choice
    config.apply_and_restart()


# ----------------------------------------------------------------------
# Deferred (no-restart) toggle: start fullscreen
# ----------------------------------------------------------------------

def prompt_start_fullscreen(parent: QWidget, config: AppConfig) -> None:
    """
    Unlike the three toggles above, this only affects window sizing at
    the next launch, so it doesn't force an immediate restart - matching
    the original app's behavior for this specific setting.
    """
    current = "currently ON" if config.start_fullscreen else "currently OFF"
    box = QMessageBox(parent)
    box.setWindowTitle("Fullscreen Startup Configuration")
    box.setText(f"Starting in fullscreen is {current}.")
    yes_button = box.addButton("Start Fullscreen", QMessageBox.ButtonRole.YesRole)
    box.addButton("Start Normally", QMessageBox.ButtonRole.NoRole)
    cancel_button = box.addButton(QMessageBox.StandardButton.Cancel)
    box.exec()

    clicked = box.clickedButton()
    if clicked is cancel_button:
        return
    config.start_fullscreen = clicked is yes_button
    config.save()
    QMessageBox.information(
        parent,
        "Fullscreen Startup",
        "This will take effect the next time you start the program.",
    )


# ----------------------------------------------------------------------
# Category list management
# ----------------------------------------------------------------------

class ManageCategoriesDialog(QDialog):
    """
    Full add/rename/remove category list editor.

    Works on a local copy of the category list so Cancel discards every
    change made during the session; Done commits the whole batch to
    AppConfig (and disk) at once. Renaming or removing here only changes
    the known-categories list used to populate dropdowns - any recipe
    files already saved under the old name keep their text as-is (see
    categories.py; there's no database to migrate).
    """

    def __init__(self, config: AppConfig, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.config = config
        self._working_categories: List[str] = list(config.categories)

        self.setWindowTitle("Manage Categories")
        self.resize(350, 400)
        self._build_ui()
        self._refresh_list()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        edit_row = QHBoxLayout()
        add_button = QPushButton("Add")
        add_button.clicked.connect(self._add_category)
        rename_button = QPushButton("Rename")
        rename_button.clicked.connect(self._rename_category)
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(self._remove_category)
        edit_row.addWidget(add_button)
        edit_row.addWidget(rename_button)
        edit_row.addWidget(remove_button)
        layout.addLayout(edit_row)

        action_row = QHBoxLayout()
        action_row.addStretch(1)
        done_button = QPushButton("Done")
        done_button.clicked.connect(self._commit_and_close)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        action_row.addWidget(done_button)
        action_row.addWidget(cancel_button)
        layout.addLayout(action_row)

    def _refresh_list(self) -> None:
        self.list_widget.clear()
        self.list_widget.addItems(self._working_categories)

    def _add_category(self) -> None:
        name, ok = QInputDialog.getText(self, "Add Category", "New category name:")
        if not ok:
            return
        name = name.strip()
        if not name:
            return
        if any(existing.lower() == name.lower() for existing in self._working_categories):
            QMessageBox.warning(self, "Add Category", f'"{name}" already exists.')
            return
        self._working_categories.append(name)
        self._refresh_list()

    def _rename_category(self) -> None:
        item = self.list_widget.currentItem()
        if item is None:
            QMessageBox.information(
                self, "Rename Category", "Select a category to rename first."
            )
            return
        old_name = item.text()
        new_name, ok = QInputDialog.getText(
            self, "Rename Category", "New name:", text=old_name
        )
        if not ok:
            return
        new_name = new_name.strip()
        if not new_name:
            return
        collision = any(
            existing.lower() == new_name.lower() and existing != old_name
            for existing in self._working_categories
        )
        if collision:
            QMessageBox.warning(self, "Rename Category", f'"{new_name}" already exists.')
            return
        index = self._working_categories.index(old_name)
        self._working_categories[index] = new_name
        self._refresh_list()

    def _remove_category(self) -> None:
        item = self.list_widget.currentItem()
        if item is None:
            QMessageBox.information(
                self, "Remove Category", "Select a category to remove first."
            )
            return
        name = item.text()
        reply = QMessageBox.question(
            self,
            "Remove Category",
            f'Remove "{name}"? Recipes already filed under this category keep '
            f"their saved category text - only the entry in this list is removed.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._working_categories.remove(name)
            self._refresh_list()

    def _commit_and_close(self) -> None:
        self.config.categories = self._working_categories
        self.config.save()
        self.accept()
