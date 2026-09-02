"""
config.py

Handles loading, saving, and defaults for Recipe Scribe Qt's configuration.
No GUI code lives here — this module is fully unit-testable in isolation.

The config file uses configparser (mirroring the original Tkinter app) and lives,
by default, at ~/.config/recipe_scribe_qt.conf. A custom path can be supplied
(primarily for testing) via the `config_path` argument to AppConfig.__init__.
"""

from __future__ import annotations

import configparser
import os
import sys
from typing import List, Optional


DEFAULT_CONFIG_PATH = os.path.expanduser("~/.config/recipe_scribe_qt.conf")

# Starter categories seeded into a brand-new config file. Fully user-editable
# afterward via the Config menu (see categories.py / config_dialogs.py).
DEFAULT_CATEGORIES = [
    "Breakfast",
    "Lunch",
    "Dinner",
    "Dessert",
    "Sauces & Gravies",
]

_COMMENT_LINES = [
    "# The options can be changed from the GUI",
    "# If editing this file directly:",
    "# Options for UseBulletPoints are True or False (default: True)",
    "# Options for FormatFileName are True or False (default: True)",
    "# Options for UseDarkMode are True or False (default: False)",
    "# Options for StartFullscreen are True or False (default: False)",
    "# Categories is a comma-separated list, e.g. Breakfast,Lunch,Dinner,Dessert",
    "# Anything other than true or false will result in the default",
]


def _str_to_bool(value: Optional[str], default: bool) -> bool:
    """
    Parses 'True'/'true' or 'False'/'false' into a bool.

    Anything else falls back to `default`, mirroring the original app's
    documented behavior: "Anything other than true or false will result
    in the default."
    """
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    return default


class AppConfig:
    """
    Loads, holds, and saves all Recipe Scribe Qt configuration values.

    Usage:
        config = AppConfig()      # uses the default ~/.config path
        config.load()             # reads existing file, or creates one with defaults
        config.save_path
        config.use_bullet_points
        ...
        config.save()             # persist any in-memory changes to disk
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or DEFAULT_CONFIG_PATH

        # In-memory values, set to sane defaults until load() is called
        self.save_path: Optional[str] = None
        self.use_bullet_points: bool = True
        self.format_filename: bool = True
        self.dark_mode: bool = False
        self.start_fullscreen: bool = False
        self.categories: List[str] = list(DEFAULT_CATEGORIES)

        self._parser = configparser.ConfigParser(
            comment_prefixes="/", allow_no_value=True
        )
        # Preserve capitalization of option names (matches original behavior)
        self._parser.optionxform = str

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load(self) -> None:
        """
        Loads settings from disk. If the config file doesn't exist yet,
        creates it with default values first.
        """
        if os.path.exists(self.config_path):
            self._parser.read(self.config_path)
            self._read_values_from_parser()
        else:
            self._ensure_sections_exist()
            self._write_comment_block()
            self._write_current_values_to_parser()
            self._write_to_disk()
            # In-memory values are already at their __init__ defaults

    def _read_values_from_parser(self) -> None:
        p = self._parser

        raw_save_path = p.get("DefaultSavePath", "save_path", fallback="None")
        self.save_path = None if raw_save_path in ("None", "") else raw_save_path

        self.use_bullet_points = _str_to_bool(
            p.get("UseBulletPoints", "use_bp", fallback="True"), default=True
        )
        self.format_filename = _str_to_bool(
            p.get("FormatFileName", "fn_format", fallback="True"), default=True
        )
        self.dark_mode = _str_to_bool(
            p.get("UseDarkMode", "dark_mode", fallback="False"), default=False
        )
        self.start_fullscreen = _str_to_bool(
            p.get("StartFullscreen", "fullscreen", fallback="False"), default=False
        )

        raw_categories = p.get("Categories", "list", fallback=None)
        if raw_categories:
            parsed = [c.strip() for c in raw_categories.split(",") if c.strip()]
            self.categories = parsed if parsed else list(DEFAULT_CATEGORIES)
        else:
            self.categories = list(DEFAULT_CATEGORIES)

    # ------------------------------------------------------------------
    # Saving
    # ------------------------------------------------------------------

    def save(self) -> None:
        """
        Writes the current in-memory values to disk, preserving the
        human-readable [Comments] documentation block.
        """
        self._ensure_sections_exist()
        self._write_comment_block()
        self._write_current_values_to_parser()
        self._write_to_disk()

    def apply_and_restart(self) -> None:
        """
        Persists current settings to disk, then replaces the current process
        with a fresh instance of itself so config changes take effect
        immediately. Mirrors the original app's restart-on-config-change
        behavior; call this from the GUI layer after a config change that
        requires a restart (e.g. dark mode, bullet points, filename format).
        """
        self.save()
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def _ensure_sections_exist(self) -> None:
        p = self._parser
        for section in (
            "Comments",
            "DefaultSavePath",
            "UseBulletPoints",
            "FormatFileName",
            "UseDarkMode",
            "StartFullscreen",
            "Categories",
        ):
            if not p.has_section(section):
                p.add_section(section)

    def _write_comment_block(self) -> None:
        p = self._parser
        for line in _COMMENT_LINES:
            if not p.has_option("Comments", line):
                p.set("Comments", line)

    def _write_current_values_to_parser(self) -> None:
        p = self._parser
        p.set(
            "DefaultSavePath",
            "save_path",
            self.save_path if self.save_path else "None",
        )
        p.set("UseBulletPoints", "use_bp", str(self.use_bullet_points))
        p.set("FormatFileName", "fn_format", str(self.format_filename))
        p.set("UseDarkMode", "dark_mode", str(self.dark_mode))
        p.set("StartFullscreen", "fullscreen", str(self.start_fullscreen))
        p.set("Categories", "list", ",".join(self.categories))

    def _write_to_disk(self) -> None:
        directory = os.path.dirname(self.config_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(self.config_path, "w") as configfile:
            self._parser.write(configfile)

    # ------------------------------------------------------------------
    # Category management
    # Used by both the dedicated "manage categories" Config dialog and the
    # save-time "this category is new, add it?" prompt on the main window.
    # ------------------------------------------------------------------

    def add_category(self, name: str) -> bool:
        """
        Adds a new category if it doesn't already exist (case-insensitive check).
        Returns True if it was added, False if it already existed or name is blank.
        Does not write to disk — call save() afterward.
        """
        name = name.strip()
        if not name:
            return False
        if any(existing.lower() == name.lower() for existing in self.categories):
            return False
        self.categories.append(name)
        return True

    def remove_category(self, name: str) -> bool:
        """
        Removes a category (case-insensitive match).
        Returns True if a category was removed, False if not found.
        Does not write to disk — call save() afterward.
        """
        for existing in self.categories:
            if existing.lower() == name.strip().lower():
                self.categories.remove(existing)
                return True
        return False

    def rename_category(self, old_name: str, new_name: str) -> bool:
        """
        Renames an existing category in place, preserving its position in the list.
        Returns True on success. Returns False if old_name wasn't found, new_name
        is blank, or new_name collides with a different existing category.
        Does not write to disk — call save() afterward.

        Note: this only updates the known-categories list. Any already-saved
        recipe files that reference the old category name are left untouched
        (matching the file-based, no-database philosophy) — see categories.py
        for the recipe-side helpers.
        """
        new_name = new_name.strip()
        if not new_name:
            return False
        for i, existing in enumerate(self.categories):
            if existing.lower() == old_name.strip().lower():
                collision = any(
                    j != i and other.lower() == new_name.lower()
                    for j, other in enumerate(self.categories)
                )
                if collision:
                    return False
                self.categories[i] = new_name
                return True
        return False
