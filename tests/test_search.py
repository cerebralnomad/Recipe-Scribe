"""
Tests for search.py — real temp-directory fixtures (no GUI, no Qt),
covering multi-word AND search, title/content scoping, and category
filtering.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from categories import attach_category  # noqa: E402
from search import (  # noqa: E402
    SearchError,
    browse_by_category,
    find_recipe_files,
    search_by_content,
    search_by_title,
    search_recipes,
    tokenize,
)


def write_recipe(tmp_path, filename, body, category=None):
    """Helper: writes a recipe file (optionally with a category footer) and returns its path."""
    content = attach_category(body, category) if category else body + "\n"
    path = tmp_path / filename
    path.write_text(content)
    return str(path)


# ----------------------------------------------------------------------
# tokenize
# ----------------------------------------------------------------------

def test_tokenize_splits_and_lowercases():
    assert tokenize("Red Pepper") == ["red", "pepper"]


def test_tokenize_handles_arbitrary_word_count():
    # Unlike the original app's two-word cap, any number of terms works.
    assert tokenize("red bell pepper flakes spicy") == [
        "red", "bell", "pepper", "flakes", "spicy",
    ]


def test_tokenize_collapses_extra_whitespace_and_strips():
    assert tokenize("  flour   sugar  ") == ["flour", "sugar"]


def test_tokenize_empty_query_returns_empty_list():
    assert tokenize("   ") == []


# ----------------------------------------------------------------------
# find_recipe_files
# ----------------------------------------------------------------------

def test_find_recipe_files_raises_when_path_missing():
    with pytest.raises(SearchError):
        find_recipe_files(None)


def test_find_recipe_files_raises_when_path_nonexistent(tmp_path):
    with pytest.raises(SearchError):
        find_recipe_files(str(tmp_path / "does_not_exist"))


def test_find_recipe_files_recurses_into_subfolders(tmp_path):
    write_recipe(tmp_path, "top_level.txt", "Top level recipe")
    subdir = tmp_path / "desserts"
    subdir.mkdir()
    write_recipe(subdir, "nested.txt", "Nested recipe")

    found = find_recipe_files(str(tmp_path))

    assert len(found) == 2
    assert any("nested.txt" in f for f in found)


def test_find_recipe_files_skips_hidden_files_and_dirs(tmp_path):
    write_recipe(tmp_path, "visible.txt", "Visible recipe")
    (tmp_path / ".hidden_file.txt").write_text("should be skipped")
    hidden_dir = tmp_path / ".git"
    hidden_dir.mkdir()
    (hidden_dir / "config").write_text("should also be skipped")

    found = find_recipe_files(str(tmp_path))

    assert len(found) == 1
    assert "visible.txt" in found[0]


# ----------------------------------------------------------------------
# search_recipes — basic matching / scoping
# ----------------------------------------------------------------------

def test_search_requires_query_or_category(tmp_path):
    with pytest.raises(SearchError):
        search_recipes(str(tmp_path), query="")


def test_search_by_title_matches_filename_only(tmp_path):
    write_recipe(tmp_path, "apple_pie.txt", "Ingredients: apples, sugar")
    write_recipe(tmp_path, "banana_bread.txt", "Ingredients: bananas, flour")

    results = search_by_title(str(tmp_path), "apple")

    assert len(results) == 1
    assert results[0].filename == "apple_pie.txt"


def test_search_by_title_does_not_match_content(tmp_path):
    # "apples" appears in the body of banana_bread but not its filename,
    # and not in apple_pie's filename either — only "apple_pie" contains
    # the substring "apple" in its filename.
    write_recipe(tmp_path, "apple_pie.txt", "A sweet dessert")
    write_recipe(tmp_path, "banana_bread.txt", "Contains diced apples too")

    results = search_by_title(str(tmp_path), "apple")

    assert len(results) == 1
    assert results[0].filename == "apple_pie.txt"


def test_search_by_content_matches_body_only(tmp_path):
    write_recipe(tmp_path, "apple_pie.txt", "A sweet dessert")
    write_recipe(tmp_path, "banana_bread.txt", "Contains diced apples too")

    results = search_by_content(str(tmp_path), "apples")

    assert len(results) == 1
    assert results[0].filename == "banana_bread.txt"


def test_search_both_scope_matches_either_title_or_content(tmp_path):
    write_recipe(tmp_path, "apple_pie.txt", "A sweet dessert")
    write_recipe(tmp_path, "banana_bread.txt", "Contains diced apples too")
    write_recipe(tmp_path, "meatloaf.txt", "No fruit here")

    results = search_recipes(str(tmp_path), query="apple", scope="both")

    filenames = {r.filename for r in results}
    assert filenames == {"apple_pie.txt", "banana_bread.txt"}


# ----------------------------------------------------------------------
# search_recipes — real multi-word AND support (no 2-word cap)
# ----------------------------------------------------------------------

def test_multiword_search_and_logic(tmp_path):
    write_recipe(tmp_path, "red_pepper_soup.txt", "red pepper base with cream")
    write_recipe(tmp_path, "black_pepper_steak.txt", "black pepper crust on steak")
    write_recipe(tmp_path, "cabbage_soup.txt", "red cabbage and onions")

    results = search_by_content(str(tmp_path), "red pepper")

    filenames = {r.filename for r in results}
    assert filenames == {"red_pepper_soup.txt"}


def test_multiword_search_supports_more_than_two_terms(tmp_path):
    # The original app hard-errored past two words; this should just work.
    write_recipe(tmp_path, "match.txt", "spicy red bell pepper flakes for heat")
    write_recipe(tmp_path, "partial.txt", "red bell pepper only, no heat")

    results = search_by_content(str(tmp_path), "red bell pepper flakes spicy")

    assert len(results) == 1
    assert results[0].filename == "match.txt"


def test_multiword_title_search_and_logic(tmp_path):
    write_recipe(tmp_path, "spicy_red_pepper_soup.txt", "body text")
    write_recipe(tmp_path, "red_pepper_soup.txt", "body text")

    results = search_by_title(str(tmp_path), "spicy red pepper")

    assert len(results) == 1
    assert results[0].filename == "spicy_red_pepper_soup.txt"


# ----------------------------------------------------------------------
# search_recipes — category filtering
# ----------------------------------------------------------------------

def test_category_filter_alone_browses_without_query(tmp_path):
    write_recipe(tmp_path, "cookies.txt", "Sweet treat", category="Dessert")
    write_recipe(tmp_path, "pancakes.txt", "Morning food", category="Breakfast")

    results = browse_by_category(str(tmp_path), "Dessert")

    assert len(results) == 1
    assert results[0].filename == "cookies.txt"


def test_category_filter_is_case_insensitive(tmp_path):
    write_recipe(tmp_path, "cookies.txt", "Sweet treat", category="Dessert")

    results = browse_by_category(str(tmp_path), "dessert")

    assert len(results) == 1


def test_category_filter_combined_with_text_query(tmp_path):
    write_recipe(tmp_path, "choc_cookies.txt", "chocolate chips", category="Dessert")
    write_recipe(tmp_path, "choc_cake.txt", "chocolate frosting", category="Dessert")
    write_recipe(tmp_path, "choc_pancakes.txt", "chocolate chips", category="Breakfast")

    results = search_recipes(
        str(tmp_path), query="chocolate chips", scope="content", category="Dessert"
    )

    assert len(results) == 1
    assert results[0].filename == "choc_cookies.txt"


def test_category_filter_excludes_recipes_with_no_category(tmp_path):
    write_recipe(tmp_path, "categorized.txt", "text", category="Dessert")
    write_recipe(tmp_path, "uncategorized.txt", "text")

    results = browse_by_category(str(tmp_path), "Dessert")

    assert len(results) == 1
    assert results[0].filename == "categorized.txt"


# ----------------------------------------------------------------------
# search_recipes — result metadata
# ----------------------------------------------------------------------

def test_results_include_category_metadata(tmp_path):
    write_recipe(tmp_path, "cookies.txt", "Sweet treat", category="Dessert")

    results = search_by_title(str(tmp_path), "cookies")

    assert results[0].category == "Dessert"


def test_results_have_none_category_when_recipe_uncategorized(tmp_path):
    write_recipe(tmp_path, "mystery.txt", "No category here")

    results = search_by_title(str(tmp_path), "mystery")

    assert results[0].category is None


def test_category_footer_does_not_cause_false_content_match(tmp_path):
    # A recipe filed under "Dessert" shouldn't match a content search for
    # "dessert" just because the word appears in its category footer.
    write_recipe(tmp_path, "cookies.txt", "Sweet treat with sugar", category="Dessert")

    results = search_by_content(str(tmp_path), "dessert")

    assert results == []


# ----------------------------------------------------------------------
# search_recipes — misc
# ----------------------------------------------------------------------

def test_search_is_case_insensitive(tmp_path):
    write_recipe(tmp_path, "apple_pie.txt", "Sweet APPLES and Sugar")

    results = search_by_content(str(tmp_path), "APPLES")

    assert len(results) == 1


def test_invalid_scope_raises_value_error(tmp_path):
    write_recipe(tmp_path, "a.txt", "text")
    with pytest.raises(ValueError):
        search_recipes(str(tmp_path), query="text", scope="nonsense")
