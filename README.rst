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
If you don't want bullet points before each ingredient you can disable them by 
selecting that item on the Config menu and choosing False.  
Re-enable them by changing it back to True. 

If you don't want the recipe title automatically formatted for use as the filename,
then select that option in the Config menu and choose False.  
This will cause the program to use the recipe name as written for the filename, 
including spaces and capital letters.

Any changes to the configuration require you to restart the application
for them to take effect, as the config file is read at program launch.

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



