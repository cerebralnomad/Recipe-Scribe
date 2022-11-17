
help_text = '''
Recipe Creator Usage:
=====================

First you should set your default save path using the Config menu item. 
This location is where the save dialog defaults to. 
It should be the root folder of your recipe directory.
If this is not set it will default to the folder the program resides
in and the first save of every session will result in needless navigation 
to your preferred save location.
It is also required to be set in order to use the search function.
This only needs to be set once, and it will remain the default
every time you run the program, but can be changed at any time.

Fill in the title, ingredients, and directions for your recipe.

The title of the recipe will be reformatted for use as the file 
name when saving. All capital letters will be made lower case, and 
spaces will be replaced with underscores.
This is the default save name, but you can name it what you want.

The ingredients list will be prepended with bullet points before
each item. Only place one ingredient per line.
A line is created when you press Enter, not if a long ingredient wraps
to the next line.
Blank lines in the ingredients will not have a bullet point.
If you want to keep a line in the ingredients from having a bullet
point, begin that line with a period (.).
The period will be removed automatically when the file is saved.

The directions will be automatically indented for all unnumbered lines.
If you type:

1. Preheat the oven to 350°F
Then do this first thing.

It will be saved as:

1. Preheat the oven to 350°F
   Then do this first thing. 

To prevent an unnumbered line from being indented begin the line with
a period (.).
This is useful for things like recipe notes.
The period will be removed when the file is saved.

CONFIG File Help
================

On the first launch a file named CONFIG will be created in the program directory.
The [DefaultSavePath] category is set from the GUI when you click Config in 
the menu. The default at creation is None.

If you don't want bullet points before each ingredient you can disable them by 
selecting that item on the menu and choosing False.
Re-enable them by changing it back to True. 

If you don't want the recipe title automatically formatted for use as the filename,
then select that option in the menu and choose False.
This will cause the program to use the recipe name as written for the filename, 
including spaces and capital letters.

Use the Config menu to choose dark or light theme, and whether you want the
program to start maximized to full screen or not.

Changing the bullet points, file formatting, or dark mode options will restart
the program automatically so the changes are applied immediately.
Setting the default path gives you the option to restart to apply the change.

Recipe Search
=============

You must have a default save path set to use the recipe search.
It uses this path as the location to perform the search.

Type the term you wish to search for in the entry field. Then click either the
Title Search or Ingredient Search button.
Title Search looks for the search term in all the recipe titles.
Ingredient search searches the contents of every recipe file for the search term.
Searches are not case sensitive.

Single word searches work best and title searches only support single words.
When searching for two words, results will include all files which contain both words.
This can greatly increase results in some cases.
For instance searching for red pepper, would return all the recipes that include
red pepper flakes but also recipes that call for red cabbage and black pepper, as
well as any that use red bell pepper or red wine and jalapeno peppers.
Searching for more than two words is not supported and will return an error
message as the results.

The list of filenames returned by the search will appear in the left side panel.
Clicking on a filename will display the recipe in the right side panel.
The recipe can be edited from within the program if you wish. After making any
edits, click the Save Edits button to save the changes.
The original file will be immediately overwritten with the edited version.

The Save button is disabled until you click in the box where the recipe
is displayed.

Menu Bar Help
=============

File > New (Ctrl+N) - clears all fields for entry of another recipe
File > Save (Ctrl+S) - choose the save location and save the file
File > Exit (Ctrl+Q) - exit the program

About - pops up the About message with program and license details.

Config - set the default save path and other program options.

Help - Show this help screen

Search Recipes - Switch to the recipe search function
Create New Recipe (Search page only) - Return to the recipe creation page.
'''
