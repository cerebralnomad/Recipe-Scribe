"""
search.py

Recipe search logic for Recipe Scribe Qt: multi-word title/content search
plus category filtering, extended well beyond the original Tkinter app's
single-word title search and two-word-max ingredient search.

No Qt dependencies - this reads real files from disk under a configured
root path, so it's testable against plain temp-directory fixtures and
reusable as-is from the search window GUI.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional

from categories import extract_category


class SearchError(Exception):
    """
    Raised for invalid search setup (missing/nonexistent save path), so
    the GUI layer can catch this and show a clear message rather than
    silently returning zero results.
    """


@dataclass
class SearchResult:
    """One matched recipe file, with the metadata the search window needs to display."""

    path: str
    filename: str
    category: Optional[str] = None


def tokenize(query: str) -> List[str]:
    """
    Splits a search query into lowercase whitespace-separated tokens,
    discarding empty strings. Used for AND-logic multi-word matching -
    unlike the original app, there's no cap on the number of terms.
    """
    return [token.lower() for token in query.strip().split() if token]


def find_recipe_files(root_path: Optional[str]) -> List[str]:
    """
    Recursively collects all recipe file paths under `root_path`, skipping
    hidden files/directories (dotfiles - e.g. a stray .git folder or editor
    swap file a user's recipe folder might contain).

    Raises SearchError if `root_path` is unset or doesn't exist, mirroring
    the original app's requirement that a default save path be configured
    before searching.
    """
    if not root_path:
        raise SearchError(
            "No default save path is configured. Set one in the Config menu."
        )
    if not os.path.isdir(root_path):
        raise SearchError(f"Configured save path does not exist: {root_path}")

    matches: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in filenames:
            if name.startswith("."):
                continue
            matches.append(os.path.join(dirpath, name))
    return sorted(matches)


def search_recipes(
    root_path: Optional[str],
    query: str = "",
    scope: str = "both",
    category: Optional[str] = None,
) -> List[SearchResult]:
    """
    Unified recipe search.

    Matches multi-word query terms (AND logic - every term must be found)
    against the recipe filename, its content, or both, optionally filtered
    down to a single category. This replaces the original app's separate
    "Title Search" (single word only) and "Ingredient Search" (max two
    words) with one function that scales to any number of terms.

    Args:
        root_path: Root folder to search recursively (AppConfig.save_path).
        query: Search text. May be blank if `category` is given, to browse
            every recipe in that category with no text filter.
        scope: "title" to match only the filename, "content" to match only
            the recipe body (ingredients + directions, category footer
            excluded so a category name can't cause a false content match),
            or "both" (default) to match either.
        category: If given, only recipes recorded under this category
            (case-insensitive) are included.

    Returns:
        A list of SearchResult, each carrying the file's path, filename,
        and recorded category (None if the recipe has no category set),
        so the results list can display category metadata without a
        second pass over the files.

    Raises:
        SearchError: if root_path is missing or doesn't exist, or if
            neither a query nor a category is given (nothing to search for).
    """
    if scope not in ("title", "content", "both"):
        raise ValueError(f"Invalid scope: {scope!r}")

    tokens = tokenize(query)
    if not tokens and not category:
        raise SearchError("Enter a search term or choose a category to browse.")

    results: List[SearchResult] = []

    for filepath in find_recipe_files(root_path):
        filename = os.path.basename(filepath)
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                raw_contents = f.read()
        except OSError:
            # Unreadable file (permissions, race condition, etc.) - skip it
            # rather than aborting the whole search.
            continue

        body, file_category = extract_category(raw_contents)

        if category and (
            file_category is None
            or file_category.lower() != category.strip().lower()
        ):
            continue

        if tokens:
            haystacks = []
            if scope in ("title", "both"):
                haystacks.append(filename.lower())
            if scope in ("content", "both"):
                haystacks.append(body.lower())
            combined = "\n".join(haystacks)
            if not all(token in combined for token in tokens):
                continue

        results.append(
            SearchResult(path=filepath, filename=filename, category=file_category)
        )

    return results


def search_by_title(
    root_path: Optional[str], query: str, category: Optional[str] = None
) -> List[SearchResult]:
    """Convenience wrapper: title-only search. See search_recipes()."""
    return search_recipes(root_path, query=query, scope="title", category=category)


def search_by_content(
    root_path: Optional[str], query: str, category: Optional[str] = None
) -> List[SearchResult]:
    """
    Convenience wrapper: content-only search (ingredients + directions).
    Corresponds to the original app's "Ingredient Search". See
    search_recipes().
    """
    return search_recipes(root_path, query=query, scope="content", category=category)


def browse_by_category(root_path: Optional[str], category: str) -> List[SearchResult]:
    """Convenience wrapper: every recipe in a given category, no text query."""
    return search_recipes(root_path, query="", scope="both", category=category)
