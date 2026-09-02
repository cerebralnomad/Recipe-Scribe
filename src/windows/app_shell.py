"""
windows/app_shell.py

The top-level application window. Hosts the recipe entry page and the
search page in a QStackedWidget, and shares a single QMenuBar between the
two - whichever page is active installs its own menu structure via its
install_menu() method (see main_window.py / search_window.py), and the
shell clears and rebuilds the menu bar each time it switches pages.

This is the piece both pages anticipated when they were first written as
standalone QMainWindows: their central-widget layout and public methods
didn't need to change, only the menu-building and top-level window
plumbing moved here.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from config import AppConfig
from windows.main_window import RecipeEntryPage
from windows.search_window import RecipeSearchPage


class AppShell(QMainWindow):
    """Top-level window hosting both pages behind a shared menu bar."""

    def __init__(self, config: AppConfig):
        super().__init__()
        self.config = config
        self.setWindowTitle("Recipe Scribe")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.entry_page = RecipeEntryPage(
            config, on_search_requested=self.show_search_page
        )
        self.search_page = RecipeSearchPage(
            config, on_new_recipe_requested=self.show_entry_page
        )

        self.stack.addWidget(self.entry_page)
        self.stack.addWidget(self.search_page)

        self.show_entry_page()

    def show_entry_page(self) -> None:
        # Categories may have changed via Manage Categories while the
        # search page was active in a future version of this flow, or via
        # direct AppConfig edits - refresh defensively rather than assume
        # the entry page's dropdown is still current.
        self.entry_page.refresh_category_widgets()
        self.stack.setCurrentWidget(self.entry_page)
        self._install_menu_for(self.entry_page)
        self.entry_page.title_entry.setFocus()

    def show_search_page(self) -> None:
        # Categories may have changed via the entry page's Config menu
        # since the search page was last shown - refresh both of its
        # dropdowns so they reflect the current list, not a stale snapshot
        # taken when the page was first constructed.
        self.search_page.refresh_category_widgets()
        self.stack.setCurrentWidget(self.search_page)
        self._install_menu_for(self.search_page)
        self.search_page.search_entry.setFocus()

    def _install_menu_for(self, page) -> None:
        menu_bar = self.menuBar()
        menu_bar.clear()
        page.install_menu(menu_bar)
