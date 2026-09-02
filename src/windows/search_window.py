"""
windows/search_window.py

The search page: a single search box with a scope selector (Title /
Content / Both) and a category filter, results list on the left, and a
recipe display/edit pane on the right - wired to search.py and
categories.py.

Like main_window.py, this is now a QWidget "page" (rather than a
standalone QMainWindow) so AppShell can host it inside a QStackedWidget
alongside the recipe entry page, sharing one menu bar between the two.

Design note on editing: the category is shown and changed via its own
QComboBox in the edit pane, not as inline "Category:" text in the body
edit box. The body box only ever shows/edits the recipe content itself
(categories.extract_category / attach_category do the split on load and
recombination on save), matching the same category-as-dropdown approach
used on the recipe entry page.
"""

from __future__ import annotations

from typing import Callable, Dict, Optional

from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenuBar,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import Qt

from config import AppConfig
from categories import attach_category, extract_category
from search import SearchError, SearchResult, search_recipes

_ALL_CATEGORIES = "All Categories"
_SCOPE_LABELS = {"Title": "title", "Content": "content", "Both": "both"}


class RecipeSearchPage(QWidget):
    """
    The recipe search/browse page.

    `on_new_recipe_requested`, if given, is called when the user chooses
    "Create New Recipe" from the menu - AppShell wires this to switch the
    QStackedWidget back to the recipe entry page.
    """

    def __init__(
        self,
        config: AppConfig,
        on_new_recipe_requested: Optional[Callable[[], None]] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.config = config
        self.on_new_recipe_requested = on_new_recipe_requested
        self._results_by_row: Dict[int, SearchResult] = {}
        self._current_result: Optional[SearchResult] = None

        self._build_ui()
        self.search_entry.setFocus()

    # ------------------------------------------------------------------
    # Menu bar (installed by the shell into its shared QMenuBar)
    # ------------------------------------------------------------------

    def install_menu(self, menu_bar: QMenuBar) -> None:
        """
        Populates a shared QMenuBar with this page's menu structure.
        AppShell calls this each time it switches to this page, after
        clearing whatever the previous page installed.
        """
        new_recipe_action = QAction("Create New Recipe", self)
        new_recipe_action.triggered.connect(self._request_new_recipe)
        menu_bar.addAction(new_recipe_action)

        quit_action = QAction("Quit", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(lambda: self.window().close())
        menu_bar.addAction(quit_action)

    def _request_new_recipe(self) -> None:
        if self.on_new_recipe_requested is not None:
            self.on_new_recipe_requested()

    # ------------------------------------------------------------------
    # Central widget
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer_layout = QVBoxLayout(self)

        outer_layout.addLayout(self._build_search_controls())

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._build_results_panel())
        splitter.addWidget(self._build_display_panel())
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        outer_layout.addWidget(splitter, stretch=1)

    def _build_search_controls(self) -> QHBoxLayout:
        row = QHBoxLayout()

        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search term (any number of words)")
        self.search_entry.setToolTip(
            "Leave blank to browse a category with no text filter"
        )
        self.search_entry.returnPressed.connect(self.run_search)

        self.scope_combo = QComboBox()
        self.scope_combo.addItems(list(_SCOPE_LABELS.keys()))
        self.scope_combo.setCurrentText("Both")
        self.scope_combo.setToolTip("Search the title, the recipe content, or both")

        self.category_filter_combo = QComboBox()
        self._refresh_category_filter_items()
        self.category_filter_combo.setToolTip("Filter results to a single category")

        search_button = QPushButton("Search")
        search_button.clicked.connect(self.run_search)

        row.addWidget(QLabel("Search:"))
        row.addWidget(self.search_entry, stretch=1)
        row.addWidget(QLabel("Scope:"))
        row.addWidget(self.scope_combo)
        row.addWidget(QLabel("Category:"))
        row.addWidget(self.category_filter_combo)
        row.addWidget(search_button)
        return row

    def _build_results_panel(self) -> QWidget:
        group = QGroupBox("Search Results")
        layout = QVBoxLayout(group)
        self.results_list = QListWidget()
        self.results_list.currentRowChanged.connect(self._on_result_selected)
        layout.addWidget(self.results_list)
        return group

    def _build_display_panel(self) -> QWidget:
        group = QGroupBox("Recipe Selected")
        layout = QGridLayout(group)

        category_label = QLabel("Category")
        self.edit_category_combo = QComboBox()
        self.edit_category_combo.setEditable(True)
        self.edit_category_combo.addItems(self.config.categories)
        self.edit_category_combo.setCurrentIndex(-1)
        self.edit_category_combo.currentTextChanged.connect(self._on_edit_changed)

        self.save_button = QPushButton("Save Edits")
        self.save_button.setEnabled(False)
        self.save_button.setToolTip(
            "Overwrites the original file immediately - there is no confirmation"
        )
        self.save_button.clicked.connect(self.save_edits)

        self.display_edit = QPlainTextEdit()
        self.display_edit.setEnabled(False)
        self.display_edit.textChanged.connect(self._on_edit_changed)

        layout.addWidget(category_label, 0, 0)
        layout.addWidget(self.edit_category_combo, 0, 1)
        layout.addWidget(self.save_button, 0, 2)
        layout.addWidget(self.display_edit, 1, 0, 1, 3)
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(1, 1)
        return group

    def refresh_category_widgets(self) -> None:
        """
        Repopulates both category dropdowns (filter and edit) from the
        current config. Called by AppShell after categories are added,
        renamed, or removed via the recipe entry page's Config menu, so
        both pages stay in sync without needing separate config objects.
        """
        current_filter = self.category_filter_combo.currentText()
        self._refresh_category_filter_items()
        if current_filter and current_filter != _ALL_CATEGORIES:
            self.category_filter_combo.setCurrentText(current_filter)

        current_edit = self.edit_category_combo.currentText()
        self.edit_category_combo.clear()
        self.edit_category_combo.addItems(self.config.categories)
        self.edit_category_combo.setCurrentText(current_edit)

    def _refresh_category_filter_items(self) -> None:
        self.category_filter_combo.clear()
        self.category_filter_combo.addItem(_ALL_CATEGORIES)
        self.category_filter_combo.addItems(self.config.categories)

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def run_search(self) -> None:
        """
        Runs a search against the configured save path using the current
        search box text, scope, and category filter, and populates the
        results list. Shows a message box for setup errors (no save path
        configured, or neither a query nor a category given) rather than
        silently returning nothing.
        """
        query = self.search_entry.text()
        scope = _SCOPE_LABELS[self.scope_combo.currentText()]
        selected_category = self.category_filter_combo.currentText()
        category = None if selected_category == _ALL_CATEGORIES else selected_category

        try:
            results = search_recipes(
                self.config.save_path, query=query, scope=scope, category=category
            )
        except SearchError as e:
            QMessageBox.warning(self, "Search", str(e))
            return

        self._populate_results(results)

    def _populate_results(self, results: list) -> None:
        self.results_list.clear()
        self._results_by_row.clear()
        self._clear_display()

        for row, result in enumerate(results):
            label = result.filename
            if result.category:
                label = f"{result.filename}  [{result.category}]"
            item = QListWidgetItem(label)
            self.results_list.addItem(item)
            self._results_by_row[row] = result

        if not results:
            self.results_list.addItem("No matching recipes found.")

    # ------------------------------------------------------------------
    # Recipe display / edit
    # ------------------------------------------------------------------

    def _on_result_selected(self, row: int) -> None:
        result = self._results_by_row.get(row)
        if result is None:
            return

        try:
            with open(result.path, "r", encoding="utf-8", errors="ignore") as f:
                raw_contents = f.read()
        except OSError as e:
            QMessageBox.warning(self, "Open Recipe", f"Could not open file:\n{e}")
            return

        body, category = extract_category(raw_contents)

        self._current_result = result
        self._loading_display = True  # suppress the "unsaved edit" signal while populating
        self.display_edit.setPlainText(body)
        self.display_edit.setEnabled(True)
        if category:
            self.edit_category_combo.setCurrentText(category)
        else:
            self.edit_category_combo.setCurrentIndex(-1)
        self._loading_display = False
        self.save_button.setEnabled(False)

    def _on_edit_changed(self) -> None:
        # Ignore signals fired while _on_result_selected is populating the
        # fields, so the Save button only enables on an actual user edit.
        if getattr(self, "_loading_display", False):
            return
        if self._current_result is not None:
            self.save_button.setEnabled(True)

    def _clear_display(self) -> None:
        self._current_result = None
        self._loading_display = True
        self.display_edit.clear()
        self.display_edit.setEnabled(False)
        self.edit_category_combo.setCurrentIndex(-1)
        self._loading_display = False
        self.save_button.setEnabled(False)

    def save_edits(self) -> None:
        """
        Overwrites the original recipe file with the edited body and
        category. No confirmation dialog, matching the original app's
        documented behavior.
        """
        if self._current_result is None:
            return

        new_category = self.edit_category_combo.currentText().strip() or None
        new_body = self.display_edit.toPlainText()
        full_text = attach_category(new_body, new_category)

        try:
            with open(self._current_result.path, "w", encoding="utf-8") as f:
                f.write(full_text)
        except OSError as e:
            QMessageBox.warning(self, "Save Edits", f"Could not save file:\n{e}")
            return

        self._current_result.category = new_category
        self.save_button.setEnabled(False)
