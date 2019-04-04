Recipe Creator
==============

Gui program for writing recipe files and saving them to a local directory.

Development
-----------

1. Ensure ``python3.6`` and ``tkiinter`` are installed
2. Clone repository: ``git clone git@github.com:cerebralnomad/gui-recipe-creator``

Usage
-----

On the first run of the program a file named CONFIG will be created in the directory 
where the program resides.
Click Config in the menu to set your default save path. 
This will be where the save dialog starts when saving a file and should be the root 
directory of your recipe folder.
Not setting this will cause the save dialog to default to the program folder and require 
unnecessary navigation to the desired directory to save the first file each session.

Fill out the recipe title, the ingredients, and the directions in the main window.
Use File>Save or Ctrl+s to save.

The recipe title will be reformatted for use as the file name. 
It will be converted to all lower case and spaces will be changed to underscores.

A bullet point will be added before each ingredient.
Both of these features can be turned off by opening the CONFIG file in a text editor 
and changing the relevant settings from True to False

After saving use File>New or Ctrl+n to clear the entry boxes for the creation of 
another recipe.
Program help can be found in the Menu

Notes
-----

Earlier versions were found to problematic with dark themes on certain distros and 
with some resolutions.
Revisions were made that forces a color palette regardless of system theme and
calculates initial window size based on screen geometry.

The entry boxes now scale properly when resizing the window.



