"""
Tests for formatting.py — no GUI, no Qt, just pure string transformations.

Several cases are drawn directly from the original README's documented
examples, to guard against regressions when porting from Tkinter.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from formatting import (  # noqa: E402
    format_filename,
    format_ingredients,
    format_directions,
)


# ----------------------------------------------------------------------
# format_filename
# ----------------------------------------------------------------------

def test_filename_formatting_enabled_lowercases_and_underscores():
    assert format_filename("Grandma's Apple Pie") == "grandma's_apple_pie"


def test_filename_formatting_disabled_uses_title_as_typed():
    assert format_filename("Grandma's Apple Pie", format_enabled=False) == "Grandma's Apple Pie"


def test_filename_formatting_strips_whitespace_regardless_of_flag():
    assert format_filename("  Spaced Title  ") == "spaced_title"
    assert format_filename("  Spaced Title  ", format_enabled=False) == "Spaced Title"


def test_filename_formatting_collapses_only_spaces_not_other_whitespace():
    # Matches original behavior: only literal spaces become underscores.
    assert format_filename("Two  Spaces") == "two__spaces"


# ----------------------------------------------------------------------
# format_ingredients
# ----------------------------------------------------------------------

def test_ingredients_readme_example():
    # Straight from the README's "Ingredients Example".
    ingredients = [
        "ingredient 1",
        "ingredient 2",
        "ingredient 3",
        "",
        ".For the Gravy",
        "gravy ingredient 1",
        "gravy ingredient 2",
    ]
    expected = [
        "• ingredient 1",
        "• ingredient 2",
        "• ingredient 3",
        "",
        "For the Gravy",
        "• gravy ingredient 1",
        "• gravy ingredient 2",
    ]
    assert format_ingredients(ingredients) == expected


def test_ingredients_accepts_newline_delimited_string():
    text = "flour\nsugar\n.Notes\nuse cake flour if possible"
    expected = [
        "• flour",
        "• sugar",
        "Notes",
        "• use cake flour if possible",
    ]
    assert format_ingredients(text) == expected


def test_ingredients_bullets_disabled_still_strips_leading_period():
    ingredients = ["salt", ".For the Sauce", "pepper"]
    expected = ["salt", "For the Sauce", "pepper"]
    assert format_ingredients(ingredients, use_bullets=False) == expected


def test_ingredients_blank_lines_never_get_bullets():
    ingredients = ["salt", "", "pepper"]
    expected = ["• salt", "", "• pepper"]
    assert format_ingredients(ingredients) == expected


# ----------------------------------------------------------------------
# format_directions
# ----------------------------------------------------------------------

def test_directions_readme_example():
    # Straight from the README's "Directions example".
    directions = [
        "1. This is the first step.",
        "This is another part of the first step",
        "",
        "2. This is the second step.",
        "A continuation of the second step.",
        "",
        ".Link to the recipe or youtube video",
    ]
    expected = [
        "1. This is the first step.",
        "   This is another part of the first step",
        "",
        "2. This is the second step.",
        "   A continuation of the second step.",
        "",
        "Link to the recipe or youtube video",
    ]
    assert format_directions(directions) == expected


def test_directions_ten_plus_steps_regression():
    # This is the bug being fixed: the original app hardcoded a 3-space
    # indent, which misaligns continuation lines once a step number
    # reaches double digits ("10. " is 4 characters wide, not 3).
    directions = [
        "9. Ninth step.",
        "Continuation of ninth step",
        "10. Tenth step.",
        "Continuation of tenth step",
    ]
    expected = [
        "9. Ninth step.",
        "   Continuation of ninth step",   # 3-space indent for single digit
        "10. Tenth step.",
        "    Continuation of tenth step",  # 4-space indent for double digit
    ]
    assert format_directions(directions) == expected


def test_directions_indent_matches_extra_whitespace_after_period():
    # If the user typed extra spaces after the period, the continuation
    # indent follows the actual prefix width rather than assuming a
    # single space.
    directions = ["1.   Wide-spaced step.", "Continuation line"]
    expected = ["1.   Wide-spaced step.", "     Continuation line"]
    assert format_directions(directions) == expected


def test_directions_fallback_indent_before_first_numbered_step():
    # Un-numbered directions (no step numbers at all) fall back to the
    # original app's default 3-space indent — applied to every line,
    # including the first, since none of them start with a digit.
    directions = ["Preheat the oven", "Then mix everything together"]
    expected = ["   Preheat the oven", "   Then mix everything together"]
    assert format_directions(directions) == expected


def test_directions_blank_lines_pass_through_untouched():
    directions = ["1. Step one.", "", "Continuation"]
    expected = ["1. Step one.", "", "   Continuation"]
    assert format_directions(directions) == expected


def test_directions_accepts_newline_delimited_string():
    text = "1. Step one.\nContinuation"
    expected = ["1. Step one.", "   Continuation"]
    assert format_directions(text) == expected
