
help_text = '''
Recipe Creator Usage:
=====================

First you should set your default save path using the Config menu item. 
This location is where the save dialog defaults to. 
It should be the root folder of your recipe directory.
If this is not set it will default to the folder the program resides
in and the first save of every session will result in needless navigation 
to your preferred save location.
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

CONFIG File Help
================

On the first launch a file named CONFIG will be created in the program directory.
The [DefaultSavePath] category is set from the GUI when you click Config in 
the menu. The default at creation is None.
You can change two other program functions by manually editing the CONFIG file 
in a text editor.

If you don't want bullet points before each ingredient you can disable them by 
changing the value of use_bp to False.
Re-enable them by changing it back to True. 

If you don't want the recipe title automatically formatted for use as the filename,
change the fn_format value to False.
This will cause the program to use the recipe name as written for the filename, 
including spaces and capital letters.

Menu Help
=========

File > New - clears all fields for entry of another recipe
File > Save - choose the save location and save the file
File > Exit - exit the program

About - pops up the About message with program and license details.

Config - set the default save path.

Help - Show this help screen
'''