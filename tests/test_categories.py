"""
Tests for categories.py — no GUI, no Qt, just per-recipe-file category
footer parsing and writing.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from categories import (  # noqa: E402
    attach_category,
    extract_category,
    has_category,
    replace_category,
    format_category_footer,
    BLANK_LINES_BEFORE_CATEGORY,
)


# ----------------------------------------------------------------------
# attach_category / format_category_footer
# ----------------------------------------------------------------------

def test_attach_category_appends_expected_blank_line_count():
    body = "Some recipe text."
    result = attach_category(body, "Dessert")

    lines = result.split("\n")
    category_index = lines.index("Category: Dessert")
    blank_lines_before = category_index - lines.index("Some recipe text.") - 1

    assert blank_lines_before == BLANK_LINES_BEFORE_CATEGORY


def test_attach_category_exact_format():
    body = "Some recipe text."
    expected = body + ("\n" * (BLANK_LINES_BEFORE_CATEGORY + 1)) + "Category: Dessert\n"
    assert attach_category(body, "Dessert") == expected


def test_attach_category_none_returns_body_unchanged():
    body = "Some recipe text."
    assert attach_category(body, None) == "Some recipe text.\n"


def test_attach_category_blank_string_returns_body_unchanged():
    body = "Some recipe text."
    assert attach_category(body, "   ") == "Some recipe text.\n"


def test_attach_category_normalizes_trailing_newlines_in_body():
    body = "Some recipe text.\n\n\n"
    result = attach_category(body, "Dessert")
    assert result.startswith("Some recipe text." + "\n" * (BLANK_LINES_BEFORE_CATEGORY + 1))


def test_attach_category_strips_category_whitespace():
    body = "Some recipe text."
    result = attach_category(body, "  Dessert  ")
    assert result.endswith("Category: Dessert\n")


# ----------------------------------------------------------------------
# extract_category
# ----------------------------------------------------------------------

def test_extract_category_round_trip():
    body = "Title\n\nIngredients\n\n• flour\n\nDirections\n\n1. Mix."
    full_text = attach_category(body, "Baking")

    extracted_body, extracted_category = extract_category(full_text)

    assert extracted_category == "Baking"
    assert extracted_body == body + "\n"


def test_extract_category_no_footer_present():
    body = "Just a plain recipe file with no category footer at all."
    extracted_body, category = extract_category(body)

    assert category is None
    assert extracted_body == body


def test_extract_category_tolerates_different_blank_line_counts():
    # Simulate a hand-edited file, or one written with a different
    # blank-line convention than the current default.
    text = "Recipe body here.\n\n\nCategory: Dinner\n"
    body, category = extract_category(text)

    assert category == "Dinner"
    assert body == "Recipe body here.\n"


def test_extract_category_case_insensitive():
    text = "Recipe body.\n\n\n\n\ncategory:   Snacks  \n"
    body, category = extract_category(text)

    assert category == "Snacks"
    assert body == "Recipe body.\n"


def test_extract_category_handles_no_blank_lines_before_footer():
    text = "Recipe body.\nCategory: Lunch\n"
    body, category = extract_category(text)

    assert category == "Lunch"
    assert body == "Recipe body.\n"


def test_extract_category_empty_category_value_treated_as_none():
    text = "Recipe body.\n\n\n\n\nCategory:\n"
    body, category = extract_category(text)

    assert category is None
    assert body == "Recipe body.\n"


# ----------------------------------------------------------------------
# has_category
# ----------------------------------------------------------------------

def test_has_category_true_when_present():
    text = attach_category("Some recipe.", "Dessert")
    assert has_category(text) is True


def test_has_category_false_when_absent():
    assert has_category("Some recipe with no footer.") is False


# ----------------------------------------------------------------------
# replace_category
# ----------------------------------------------------------------------

def test_replace_category_updates_existing():
    original = attach_category("Some recipe.", "Dessert")
    updated = replace_category(original, "Breakfast")

    body, category = extract_category(updated)
    assert category == "Breakfast"
    assert body == "Some recipe.\n"


def test_replace_category_adds_when_missing():
    original = "Some recipe with no category yet."
    updated = replace_category(original, "Lunch")

    body, category = extract_category(updated)
    assert category == "Lunch"
    assert body == "Some recipe with no category yet.\n"


def test_replace_category_removes_when_set_to_none():
    original = attach_category("Some recipe.", "Dessert")
    updated = replace_category(original, None)

    body, category = extract_category(updated)
    assert category is None
    assert body == "Some recipe.\n"
