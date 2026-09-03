"""
resources/help_text.py

Plain-text help content shown in the Help window. Adapted from the
original Tkinter app's HelpText.py, updated for the features that are new
in this version: categories and the merged multi-word search.
"""

HELP_TEXT = """
Recipe Scribe Usage
===================

First you should set your default save path using the Config menu item.
This location is where the save dialog defaults to.
It should be the root folder of your recipe directory.
If this is not set it will default to wherever the save dialog last was,
and the first save of every session will result in needless navigation
to your preferred save location.
It is also required to be set in order to use the search function.
This only needs to be set once, and it will remain the default every
time you run the program, but can be changed at any time.

Fill in the title, category, ingredients, and directions for your recipe.

The title of the recipe will be reformatted for use as the file name when
saving. All capital letters will be made lower case, and spaces will be
replaced with underscores. This is the default save name, but you can
name it whatever you want in the save dialog.

Category
========

Choose a category from the dropdown, or type a new one directly into the
box. If you type a category that isn't in your list yet, you'll be asked
whether to add it when you save. You can also manage your category list
at any time from the Config menu (add, rename, or remove categories).

Renaming or removing a category only changes the list you pick from -
recipes you've already saved keep whatever category text was written
into them at the time.

Ingredients
===========

The ingredients list will be prepended with bullet points before each
item. Only place one ingredient per line. A line is created when you
press Enter, not if a long ingredient wraps to the next line.
Blank lines in the ingredients will not have a bullet point.
If you want to keep a line in the ingredients from having a bullet point,
begin that line with a period (.). The period will be removed
automatically when the file is saved. This is useful for section
headers, e.g. ".For the Gravy".

Directions
==========

The directions will be automatically indented for all unnumbered lines
so they line up under the step they belong to - including step 10 and
beyond. If you type:

1. Preheat the oven to 350F
Then do this first thing.

10. This is the tenth step
And its continuation

It will be saved as:

1. Preheat the oven to 350F
   Then do this first thing.

10. This is the tenth step
    And its continuation

To prevent an unnumbered line from being indented, begin the line with a
period (.). This is useful for things like recipe notes or links.
The period will be removed when the file is saved.

After saving, use File > New or Ctrl+N to clear the entry boxes for the
creation of another recipe.

CONFIG File Help
================

On the first launch a file named recipe_scribe_qt.conf will be created in
~/.config. The DefaultSavePath is set from the GUI when you click
"Set Default Save Path" in the Config menu.

If you don't want bullet points before each ingredient, you can disable
them from the Config menu.

If you don't want the recipe title automatically formatted for use as the
filename, you can disable that from the Config menu too. This will cause
the program to use the recipe title as written for the filename,
including spaces and capital letters.

Use the Config menu to choose dark or light theme, and whether you want
the program to start maximized to full screen or not.

Changing bullet points, filename formatting, or dark mode will restart
the program automatically so the change is applied immediately - save any
unsaved recipe first. Changing the fullscreen startup setting does not
restart the program; it takes effect the next time you launch it.

Your category list is also stored in this config file, and can be managed
from the Config menu at any time.

Recipe Search
=============

You must have a default save path set to use the recipe search.
It uses this path as the location to perform the search.

Type your search term into the search box - any number of words is
supported, and a recipe must contain all of them to match. Use the Scope
dropdown to search titles only, recipe content only, or both. Use the
Category dropdown to narrow results to a single category, or leave the
search box empty and pick a category to browse everything filed under it.
Searches are not case sensitive.

Recipes created with the previous version of the program before the category
feature was implemented, will not have a category and will not be shown
in a category only search with no keywords.

The search results will display in the left hand pane, along with each
recipe's category if it has one. Click on a result and the recipe will be
displayed in the right pane. You can edit the recipe's text and category
from the program if you need to - simply make your changes and click
Save Edits. Clicking Save Edits will immediately overwrite the existing
file with the contents shown. There is no confirmation dialog.

Menu Bar Help
=============

File > New (Ctrl+N) - clears all fields for entry of another recipe
File > Save (Ctrl+S) - choose the save location and save the file
File > Quit (Ctrl+Q) - exit the program

Config > Set Default Save Path - choose where recipes are saved/searched
Config > Manage Categories - add, rename, or remove categories
Config > Use Bullet Points / Format Filename / Use Dark Mode / Start
Fullscreen - toggle these settings

Help > Program Help (Ctrl+H) - show this help screen
Help > About - version and license details

Search Recipes - switch to the recipe search page
Create New Recipe (search page only) - return to the recipe entry page
"""
