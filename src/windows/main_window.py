"""
windows/main_window.py

The recipe entry page: Title / Category / Ingredients / Directions, with
File (New/Save/Quit) and Config menu actions.

As anticipated when this module was first written, it's now a QWidget
("page") rather than a standalone QMainWindow, so AppShell
(windows/app_shell.py) can host it inside a QStackedWidget alongside the
search page and share one menu bar between the two. Nothing about the
central layout or the public method names (new_recipe, save_recipe, the
title/category/ingredients/directions attributes) changed in this
refactor - only the menu-building and top-level window plumbing moved.

Note on saved file layout: a blank line is written before the title, ahead
of Title / Ingredients / Directions each being separated by a single blank
line. This is intentional - it keeps the title from sitting flush against
the top edge of the screen when recipes are viewed on small displays, e.g.
a 7" screen in the kitchen. The Category footer is appended separately by
categories.attach_category().
"""

from __future__ import annotations

import os
from typing import Callable, Optional

from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMenuBar,
    QMessageBox,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from config import AppConfig
from categories import attach_category
from formatting import format_directions, format_filename, format_ingredients
from windows.about_window import AboutWindow
from windows.config_dialogs import (
    ManageCategoriesDialog,
    prompt_dark_mode,
    prompt_format_filename,
    prompt_set_default_save_path,
    prompt_start_fullscreen,
    prompt_use_bullet_points,
)
from windows.help_window import HelpWindow


class RecipeEntryPage(QWidget):
    """
    The recipe entry page.

    `on_search_requested`, if given, is called when the user chooses
    "Search Recipes" from the menu - AppShell wires this to switch the
    QStackedWidget to the search page.
    """

    def __init__(
        self,
        config: AppConfig,
        on_search_requested: Optional[Callable[[], None]] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.config = config
        self.on_search_requested = on_search_requested

        self._build_ui()
        self._apply_tab_order()
        self.title_entry.setFocus()

    # ------------------------------------------------------------------
    # Menu bar (installed by the shell into its shared QMenuBar)
    # ------------------------------------------------------------------

    def install_menu(self, menu_bar: QMenuBar) -> None:
        """
        Populates a shared QMenuBar with this page's menu structure.
        AppShell calls this each time it switches to this page, after
        clearing whatever the previous page installed.
        """
        file_menu = menu_bar.addMenu("&File")

        new_action = QAction("New", self)
        new_action.setShortcut(QKeySequence("Ctrl+N"))
        new_action.triggered.connect(self.new_recipe)
        file_menu.addAction(new_action)

        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.save_recipe)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(lambda: self.window().close())
        file_menu.addAction(quit_action)

        config_menu = menu_bar.addMenu("&Config")

        set_path_action = QAction("Set Default Save Path", self)
        set_path_action.triggered.connect(self._set_default_save_path)
        config_menu.addAction(set_path_action)

        config_menu.addSeparator()

        self.bullet_points_action = QAction("", self)
        self.bullet_points_action.triggered.connect(self._prompt_bullet_points)
        config_menu.addAction(self.bullet_points_action)

        self.filename_format_action = QAction("", self)
        self.filename_format_action.triggered.connect(self._prompt_filename_format)
        config_menu.addAction(self.filename_format_action)

        self.dark_mode_action = QAction("", self)
        self.dark_mode_action.triggered.connect(self._prompt_dark_mode)
        config_menu.addAction(self.dark_mode_action)

        self.fullscreen_action = QAction("", self)
        self.fullscreen_action.triggered.connect(self._prompt_fullscreen)
        config_menu.addAction(self.fullscreen_action)

        config_menu.addSeparator()

        manage_categories_action = QAction("Manage Categories", self)
        manage_categories_action.triggered.connect(self._manage_categories)
        config_menu.addAction(manage_categories_action)

        self._refresh_toggle_labels()

        help_menu = menu_bar.addMenu("&Help")

        help_action = QAction("Program Help", self)
        help_action.setShortcut(QKeySequence("Ctrl+H"))
        help_action.triggered.connect(self._show_help)
        help_menu.addAction(help_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        search_action = QAction("Search Recipes", self)
        search_action.triggered.connect(self._request_search)
        menu_bar.addAction(search_action)

    def _request_search(self) -> None:
        if self.on_search_requested is not None:
            self.on_search_requested()

    def _refresh_toggle_labels(self) -> None:
        """
        Updates the Config menu's toggle labels to show the current
        value, e.g. "Use Bullet Points (True)". Three of the four toggles
        restart the program immediately on change, so in practice this
        only needs to run once at startup for those - but fullscreen
        doesn't restart, so its label is refreshed after every change too.
        """
        self.bullet_points_action.setText(
            f"Use Bullet Points ({self.config.use_bullet_points})"
        )
        self.filename_format_action.setText(
            f"Format Filename ({self.config.format_filename})"
        )
        self.dark_mode_action.setText(f"Use Dark Mode ({self.config.dark_mode})")
        self.fullscreen_action.setText(
            f"Start Fullscreen ({self.config.start_fullscreen})"
        )

    # ------------------------------------------------------------------
    # Central widget
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QGridLayout(self)

        title_label = QLabel("Recipe Title")
        self.title_entry = QLineEdit()
        self.title_entry.setToolTip("Enter the title of the recipe here")

        category_label = QLabel("Category")
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItems(self.config.categories)
        self.category_combo.setCurrentIndex(-1)  # no category selected by default
        self.category_combo.setToolTip(
            "Choose a category, or type a new one to add it on save"
        )

        layout.addWidget(title_label, 0, 0)
        layout.addWidget(self.title_entry, 0, 1)
        layout.addWidget(category_label, 0, 2)
        layout.addWidget(self.category_combo, 0, 3)

        ing_group = QGroupBox("Ingredients")
        ing_layout = QVBoxLayout(ing_group)
        self.ingredients_edit = QPlainTextEdit()
        self.ingredients_edit.setToolTip(
            "Enter ingredients here, one per line\n"
            "Begin a line with a period to omit the bullet point"
        )
        ing_layout.addWidget(self.ingredients_edit)
        layout.addWidget(ing_group, 1, 0, 1, 2)

        dir_group = QGroupBox("Directions")
        dir_layout = QVBoxLayout(dir_group)
        self.directions_edit = QPlainTextEdit()
        self.directions_edit.setToolTip("Enter the recipe instructions here")
        dir_layout.addWidget(self.directions_edit)
        layout.addWidget(dir_group, 1, 2, 1, 2)

        # Directions lines tend to run much longer than ingredient lines,
        # so the directions column gets twice the stretch weight -
        # roughly a 1/3 (ingredients) to 2/3 (directions) split, matching
        # the original Tkinter layout.
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 2)

    def _apply_tab_order(self) -> None:
        self.setTabOrder(self.title_entry, self.category_combo)
        self.setTabOrder(self.category_combo, self.ingredients_edit)
        self.setTabOrder(self.ingredients_edit, self.directions_edit)
        self.setTabOrder(self.directions_edit, self.title_entry)

    # ------------------------------------------------------------------
    # File actions
    # ------------------------------------------------------------------

    def new_recipe(self) -> None:
        """Clears all fields for entry of another recipe."""
        self.title_entry.clear()
        self.category_combo.setCurrentIndex(-1)
        self.ingredients_edit.clear()
        self.directions_edit.clear()
        self.title_entry.setFocus()

    def save_recipe(self) -> None:
        """
        Opens the save dialog, formats the recipe body, prompts to add an
        unrecognized category to the known list, appends the category
        footer, and writes the file.
        """
        title = self.title_entry.text()
        category = self.category_combo.currentText().strip()

        suggested_filename = format_filename(title, self.config.format_filename)
        default_dir = self.config.save_path or ""
        default_path = (
            os.path.join(default_dir, suggested_filename)
            if default_dir
            else suggested_filename
        )

        path, _ = QFileDialog.getSaveFileName(
            self, "Save Recipe", default_path, "Text Files (*.txt);;All Files (*)"
        )
        if not path:
            return  # user cancelled

        if category:
            self._offer_to_add_new_category(category)

        body = self._build_recipe_body(title)
        full_text = attach_category(body, category or None)

        with open(path, "w", encoding="utf-8") as f:
            f.write(full_text)

    def _offer_to_add_new_category(self, category: str) -> None:
        already_known = any(
            existing.lower() == category.lower() for existing in self.config.categories
        )
        if already_known:
            return

        reply = QMessageBox.question(
            self,
            "New Category",
            f'"{category}" is not in your category list yet. Add it?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.config.add_category(category)
            self.config.save()
            self.category_combo.addItem(category)

    def _build_recipe_body(self, title: str) -> str:
        """
        Assembles the Title/Ingredients/Directions text that gets written
        to disk, ahead of the category footer being appended separately.

        A leading blank line is included before the title on purpose -
        it keeps the title from sitting flush against the top of the
        screen when the file is viewed on a small display.
        """
        ingredient_lines = format_ingredients(
            self.ingredients_edit.toPlainText(), self.config.use_bullet_points
        )
        direction_lines = format_directions(self.directions_edit.toPlainText())

        parts = [
            "",
            title,
            "",
            "Ingredients",
            "",
            *ingredient_lines,
            "",
            "Directions",
            "",
            *direction_lines,
        ]
        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Config menu actions
    # ------------------------------------------------------------------

    def _set_default_save_path(self) -> None:
        prompt_set_default_save_path(self, self.config)

    def _prompt_bullet_points(self) -> None:
        prompt_use_bullet_points(self, self.config)
        # Unreachable in practice: prompt_use_bullet_points restarts the
        # process on any actual change via apply_and_restart(). Only a
        # Cancel returns control here, so there's nothing to refresh.

    def _prompt_filename_format(self) -> None:
        prompt_format_filename(self, self.config)

    def _prompt_dark_mode(self) -> None:
        prompt_dark_mode(self, self.config)

    def _prompt_fullscreen(self) -> None:
        prompt_start_fullscreen(self, self.config)
        # Fullscreen doesn't restart the process, so its label needs an
        # explicit refresh to reflect the new value immediately.
        self._refresh_toggle_labels()

    def _manage_categories(self) -> None:
        dialog = ManageCategoriesDialog(self.config, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.refresh_category_widgets()

    def refresh_category_widgets(self) -> None:
        """
        Repopulates the category dropdown after the known list changes.
        Called internally after Manage Categories, and by AppShell when
        switching back to this page in case categories changed elsewhere.
        """
        current_text = self.category_combo.currentText()
        self.category_combo.clear()
        self.category_combo.addItems(self.config.categories)
        self.category_combo.setCurrentText(current_text)

    # ------------------------------------------------------------------
    # Help / About
    # ------------------------------------------------------------------

    def _show_help(self) -> None:
        HelpWindow(self).exec()

    def _show_about(self) -> None:
        AboutWindow(self).exec()
