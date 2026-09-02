"""
Tests for config.py — no GUI, no Qt, just config load/save/defaults and
category list management.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from config import AppConfig, DEFAULT_CATEGORIES  # noqa: E402


def make_config(tmp_path, filename="test_recipe_scribe_qt.conf"):
    return AppConfig(config_path=str(tmp_path / filename))


# ----------------------------------------------------------------------
# First-run / defaults
# ----------------------------------------------------------------------

def test_creates_config_file_with_defaults_when_missing(tmp_path):
    config = make_config(tmp_path)
    assert not os.path.exists(config.config_path)

    config.load()

    assert os.path.exists(config.config_path)
    assert config.save_path is None
    assert config.use_bullet_points is True
    assert config.format_filename is True
    assert config.dark_mode is False
    assert config.start_fullscreen is False
    assert config.categories == DEFAULT_CATEGORIES


def test_default_config_file_is_readable_back(tmp_path):
    # Round-trip: create with defaults, then load a fresh instance from the
    # same path and confirm values match.
    first = make_config(tmp_path)
    first.load()

    second = make_config(tmp_path)
    second.load()

    assert second.save_path == first.save_path
    assert second.use_bullet_points == first.use_bullet_points
    assert second.categories == first.categories


# ----------------------------------------------------------------------
# Loading existing values
# ----------------------------------------------------------------------

def test_loads_existing_values_from_disk(tmp_path):
    config = make_config(tmp_path)
    config.load()

    config.save_path = "/home/user/Recipes"
    config.use_bullet_points = False
    config.dark_mode = True
    config.categories = ["Breakfast", "Dessert"]
    config.save()

    reloaded = make_config(tmp_path)
    reloaded.load()

    assert reloaded.save_path == "/home/user/Recipes"
    assert reloaded.use_bullet_points is False
    assert reloaded.dark_mode is True
    assert reloaded.categories == ["Breakfast", "Dessert"]


def test_boolean_parsing_invalid_value_falls_back_to_default(tmp_path):
    config = make_config(tmp_path)
    config.load()

    # Manually write a garbage value for use_bp and confirm it falls back
    # to the documented default (True) rather than raising or misparsing.
    with open(config.config_path, "a") as f:
        pass  # file already has sections from load()

    config._parser.set("UseBulletPoints", "use_bp", "banana")
    config._write_to_disk()

    reloaded = make_config(tmp_path)
    reloaded.load()
    assert reloaded.use_bullet_points is True  # fell back to default


def test_missing_categories_section_falls_back_to_defaults(tmp_path):
    # Simulate an old/hand-edited config file with no Categories section at all.
    path = tmp_path / "legacy.conf"
    path.write_text(
        "[DefaultSavePath]\n"
        "save_path = None\n"
        "\n"
        "[UseBulletPoints]\n"
        "use_bp = True\n"
    )
    config = AppConfig(config_path=str(path))
    config.load()

    assert config.categories == DEFAULT_CATEGORIES


# ----------------------------------------------------------------------
# Category management
# ----------------------------------------------------------------------

def test_add_category_success(tmp_path):
    config = make_config(tmp_path)
    config.load()

    added = config.add_category("Slow Cooker")
    assert added is True
    assert "Slow Cooker" in config.categories


def test_add_category_rejects_duplicate_case_insensitive(tmp_path):
    config = make_config(tmp_path)
    config.load()
    config.add_category("Dessert")

    added_again = config.add_category("dessert")
    assert added_again is False
    assert config.categories.count("Dessert") == 1


def test_add_category_rejects_blank(tmp_path):
    config = make_config(tmp_path)
    config.load()

    assert config.add_category("   ") is False


def test_remove_category_success(tmp_path):
    config = make_config(tmp_path)
    config.load()

    removed = config.remove_category("Breakfast")
    assert removed is True
    assert "Breakfast" not in config.categories


def test_remove_category_not_found(tmp_path):
    config = make_config(tmp_path)
    config.load()

    removed = config.remove_category("Nonexistent Category")
    assert removed is False


def test_rename_category_success(tmp_path):
    config = make_config(tmp_path)
    config.load()

    renamed = config.rename_category("Dinner", "Main Course")
    assert renamed is True
    assert "Main Course" in config.categories
    assert "Dinner" not in config.categories


def test_rename_category_preserves_position(tmp_path):
    config = make_config(tmp_path)
    config.load()
    original_index = config.categories.index("Dinner")

    config.rename_category("Dinner", "Main Course")

    assert config.categories.index("Main Course") == original_index


def test_rename_category_not_found(tmp_path):
    config = make_config(tmp_path)
    config.load()

    renamed = config.rename_category("Nonexistent", "New Name")
    assert renamed is False


def test_rename_category_rejects_collision(tmp_path):
    config = make_config(tmp_path)
    config.load()

    renamed = config.rename_category("Dinner", "Dessert")
    assert renamed is False
    assert "Dinner" in config.categories  # unchanged


def test_rename_category_rejects_blank_new_name(tmp_path):
    config = make_config(tmp_path)
    config.load()

    renamed = config.rename_category("Dinner", "   ")
    assert renamed is False
    assert "Dinner" in config.categories


def test_category_changes_persist_across_save_and_reload(tmp_path):
    config = make_config(tmp_path)
    config.load()

    config.add_category("Slow Cooker")
    config.remove_category("Lunch")
    config.rename_category("Dinner", "Main Course")
    config.save()

    reloaded = make_config(tmp_path)
    reloaded.load()

    assert "Slow Cooker" in reloaded.categories
    assert "Lunch" not in reloaded.categories
    assert "Main Course" in reloaded.categories
    assert "Dinner" not in reloaded.categories


# ----------------------------------------------------------------------
# Comment-line / round-trip corruption regression
#
# configparser treats ':' and '=' as key/value delimiters even inside a
# bare "no value" option name. A comment line containing either character
# (e.g. "(default: True)") gets silently rewritten on the very next
# read-then-save cycle, no longer matches the original string, and gets
# re-added as a duplicate - which crashes on the cycle after that with
# a real DuplicateOptionError. This exact bug reached a real user via the
# dark-mode restart flow (every restart is a read-then-save cycle) before
# being caught here.
# ----------------------------------------------------------------------

def test_comment_lines_contain_no_delimiter_characters():
    """
    Guards against ever reintroducing ':' or '=' in a comment line, since
    both are configparser's key/value delimiters and corrupt a bare-option
    comment line on a read/write round trip.
    """
    from config import _COMMENT_LINES

    for line in _COMMENT_LINES:
        assert ":" not in line, f"Comment line contains ':': {line!r}"
        assert "=" not in line, f"Comment line contains '=': {line!r}"


def test_many_repeated_load_save_cycles_do_not_corrupt_comments(tmp_path):
    """
    Regression test for the exact real-world crash: every restart after a
    dark-mode/bullet-point/filename-format toggle is a read-then-save
    cycle. This simulates 20 such cycles (the original bug surfaced by
    the third) and confirms the Comments section never grows or
    duplicates.
    """
    path = str(tmp_path / "cycle_test.conf")

    for _ in range(20):
        config = AppConfig(config_path=path)
        config.load()  # must never raise
        config.dark_mode = not config.dark_mode
        config.save()

    final_config = AppConfig(config_path=path)
    final_config.load()

    from config import _COMMENT_LINES

    with open(path) as f:
        contents = f.read()
    comments_section = contents.split("[Comments]")[1].split("[DefaultSavePath]")[0]
    comment_line_count = len(
        [line for line in comments_section.splitlines() if line.strip()]
    )
    assert comment_line_count == len(_COMMENT_LINES)


def test_corrupted_config_file_recovers_instead_of_crashing(tmp_path):
    """
    If the on-disk file is unparseable for any reason (this bug, a bad
    manual edit, a crash mid-write), load() must recover with fresh
    defaults rather than raising and taking down the whole app on launch.
    """
    path = tmp_path / "corrupted.conf"
    path.write_text(
        "[Comments]\n"
        "# The options can be changed from the GUI\n"
        "# If editing this file directly = \n"
        "# If editing this file directly:\n"
        "\n"
        "[DefaultSavePath]\n"
        "save_path = /home/user/Recipes\n"
    )

    config = AppConfig(config_path=str(path))
    config.load()  # must not raise

    # Recovered to fresh defaults rather than crashing.
    assert config.save_path is None
    assert config.use_bullet_points is True
    assert config.categories == DEFAULT_CATEGORIES

    # The file on disk is now valid and reloadable.
    reloaded = AppConfig(config_path=str(path))
    reloaded.load()
    assert reloaded.save_path is None
