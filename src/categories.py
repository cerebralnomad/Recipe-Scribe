"""
categories.py

Pure, Qt-independent helpers for reading and writing the per-recipe
category footer.

The list of known category *names* (add/remove/rename the dropdown
options) lives in AppConfig (config.py). This module only deals with a
single recipe file: does it have a category recorded, what is it, and how
do we attach/detach that footer when saving or editing.

Storage format
--------------
Recipe files created by this app end with a footer block, separated from
the recipe body by several blank lines, e.g.:

    ...
    3. Bake for 25 minutes.




    Category: Dessert

Keeping the category at the very end (rather than a header line under the
title) means the recipe body itself still looks exactly like a plain
recipe file with nothing new to read past at the top - the file stays
fully self-describing, but the metadata stays out of the way of the
recipe content itself.
"""

from __future__ import annotations

import re
from typing import Optional, Tuple

# Number of blank lines separating the recipe body from the Category line
# in files written by this app. Parsing tolerates any number of blank
# lines (see extract_category), so this only governs what gets *written*.
BLANK_LINES_BEFORE_CATEGORY = 4

_CATEGORY_LINE = re.compile(r"^\s*Category:\s*(.*?)\s*$", re.IGNORECASE)


def format_category_footer(
    category: str, blank_lines: int = BLANK_LINES_BEFORE_CATEGORY
) -> str:
    """
    Builds the footer block to append to a recipe body: the blank-line
    separator plus the "Category: <name>" line.

    This does not include the recipe body itself - use attach_category()
    to combine the two, since it also handles normalizing the body's
    trailing whitespace first.
    """
    separator = "\n" * (blank_lines + 1)
    return f"{separator}Category: {category.strip()}\n"


def attach_category(body: str, category: Optional[str]) -> str:
    """
    Appends the category footer to a recipe body, producing the full text
    that should be written to disk.

    If `category` is None or blank, the body is returned unchanged aside
    from trailing-whitespace normalization (a single trailing newline) -
    recipes can be saved without a category at all.
    """
    trimmed_body = body.rstrip("\n")
    if not category or not category.strip():
        return trimmed_body + "\n"
    return trimmed_body + format_category_footer(category)


def extract_category(file_contents: str) -> Tuple[str, Optional[str]]:
    """
    Splits a recipe file's full contents into (body, category).

    Scans lines from the end of the file for the first line matching
    "Category: <name>" (case-insensitive). Everything from that line
    onward is treated as the footer and removed, along with any blank
    lines immediately preceding it (the separator). If no such line is
    found, returns (file_contents, None) unchanged.

    Parsing is intentionally tolerant of any number of blank lines before
    the Category line - it only requires the Category line itself to be
    present. This covers hand-edited files, or files written by an
    earlier version that used a different blank-line count.
    """
    lines = file_contents.splitlines()

    category_line_index = None
    category_value = None
    for i in range(len(lines) - 1, -1, -1):
        match = _CATEGORY_LINE.match(lines[i])
        if match:
            category_line_index = i
            category_value = match.group(1).strip() or None
            break

    if category_line_index is None:
        return file_contents, None

    # Trim blank lines immediately preceding the Category line - those
    # belong to the separator, not the recipe body.
    body_end = category_line_index
    while body_end > 0 and lines[body_end - 1].strip() == "":
        body_end -= 1

    body = "\n".join(lines[:body_end]).rstrip("\n") + "\n"
    return body, category_value


def has_category(file_contents: str) -> bool:
    """Convenience check: does this recipe file have a recorded category?"""
    _, category = extract_category(file_contents)
    return category is not None


def replace_category(file_contents: str, new_category: Optional[str]) -> str:
    """
    Returns a new version of a recipe file's full contents with its
    category replaced (or removed, if `new_category` is None/blank).
    The recipe body itself is left untouched.

    Useful for the search/edit window: load a file, let the user change
    the category via a dropdown, then write this back out on Save Edits.
    """
    body, _ = extract_category(file_contents)
    return attach_category(body, new_category)
