"""
formatting.py

Pure, Qt-independent formatting functions for Recipe Scribe Qt.

Covers:
- Filename formatting (lowercase + underscores, or as-typed)
- Ingredient bullet-point formatting (with a '.'-prefix escape hatch)
- Directions auto-indentation for continuation lines (with a '.'-prefix
  escape hatch), using a dynamic indent width rather than the original
  app's hardcoded 3 spaces — see format_directions() for details.

None of this code touches the filesystem, Qt, or the app's config object —
callers pass in plain strings/lists and get plain strings/lists back, so
every function here is easily unit tested and reusable outside a GUI
context.
"""

from __future__ import annotations

import re
from typing import List, Sequence, Union

TextInput = Union[str, Sequence[str]]

_LEADING_PERIOD = re.compile(r"^\.")
_HAS_WORD_CHAR = re.compile(r"\w")
_STEP_PREFIX = re.compile(r"^(\d+\.\s*)")

_DEFAULT_INDENT = "   "  # 3 spaces — matches the original app's fallback


def _to_lines(text: TextInput) -> List[str]:
    """Accepts either a single string (split on newlines) or a list of lines."""
    if isinstance(text, str):
        return text.split("\n")
    return list(text)


# ----------------------------------------------------------------------
# Filename formatting
# ----------------------------------------------------------------------

def format_filename(title: str, format_enabled: bool = True) -> str:
    """
    Reformats a recipe title into a filesystem-friendly filename.

    When `format_enabled` is True (the default): lowercases the title and
    replaces spaces with underscores, matching the original app's behavior.

    When False: the title is used as-typed.

    Leading/trailing whitespace is always stripped, regardless of the flag.
    """
    stripped = title.strip()
    if format_enabled:
        return stripped.lower().replace(" ", "_")
    return stripped


# ----------------------------------------------------------------------
# Ingredient bullet-point formatting
# ----------------------------------------------------------------------

def format_ingredients(ingredients: TextInput, use_bullets: bool = True) -> List[str]:
    """
    Formats ingredient lines for saving to a recipe file.

    Rules (matching the original app):
    - Blank lines (or lines with no letters/numbers at all) are passed
      through untouched — no bullet is added.
    - A line starting with a period is written as-is with the leading
      period stripped, and never gets a bullet. This is the escape hatch
      for section headers, e.g. ".For the Gravy" -> "For the Gravy".
    - Every other non-blank line gets a "• " prefix when `use_bullets`
      is True.
    - When `use_bullets` is False, ordinary lines pass through unchanged,
      but '.'-prefixed lines still have their leading period stripped,
      since that's an explicit per-line instruction from the user rather
      than something the bullet-point toggle should override.
    """
    lines = _to_lines(ingredients)
    formatted: List[str] = []

    for line in lines:
        if _LEADING_PERIOD.match(line):
            formatted.append(_LEADING_PERIOD.sub("", line, count=1))
        elif not _HAS_WORD_CHAR.search(line):
            formatted.append(line)
        elif use_bullets:
            formatted.append("• " + line)
        else:
            formatted.append(line)

    return formatted


# ----------------------------------------------------------------------
# Directions auto-indentation
# ----------------------------------------------------------------------

def format_directions(directions: TextInput) -> List[str]:
    """
    Formats direction lines for saving to a recipe file.

    Rules:
    - A line starting with a number followed by a period (e.g. "1.", "10.")
      is treated as a new step and written as-is. The width of that
      number's prefix (digits + period + any following whitespace) becomes
      the indent width used for continuation lines that follow it.
    - A line starting with a period is written as-is with the leading
      period stripped, and is never indented — the escape hatch for notes
      or links.
    - Blank lines are passed through untouched.
    - Any other line is a continuation of the current step and is indented
      to match that step's prefix width.

    This fixes a bug in the original Tkinter app, where continuation lines
    were always indented with a hardcoded 3 spaces. That looked fine for
    steps 1-9 (whose "N. " prefix is exactly 3 characters), but produced
    misaligned output from step 10 onward, since "10. " is 4 characters
    wide. Here the indent width is derived from the actual prefix of the
    most recent step line, so alignment stays correct at any step count.

    Before the first numbered step appears, continuation-style lines fall
    back to a default 3-space indent, matching the original's behavior for
    un-numbered directions.
    """
    lines = _to_lines(directions)
    formatted: List[str] = []
    current_indent = _DEFAULT_INDENT

    for line in lines:
        step_match = _STEP_PREFIX.match(line)
        if step_match:
            current_indent = " " * len(step_match.group(1))
            formatted.append(line)
        elif _LEADING_PERIOD.match(line):
            formatted.append(_LEADING_PERIOD.sub("", line, count=1))
        elif not _HAS_WORD_CHAR.search(line):
            formatted.append(line)
        else:
            formatted.append(current_indent + line)

    return formatted
