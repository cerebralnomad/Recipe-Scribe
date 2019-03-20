# gui_recipe_creator
A no frills recipe program. Creates recipe files in text format without a database and saves to the specified location.  
Programmed in Python 3.6

![Screenshot](/screenshot/rc_main_window.png?raw=true "Screenshot")

## Installation

You can download the recipe_creator_linux_executable tarball for a standalone executable for Linux made with Pyinstaller.
No Windows exe, but you're welcome to make your own using the source files on windows.

Otherwise either clone the repo or download the recipe_creator_source_files tarball.
Make recipe_creator.py executable and run from the command line or make a program shortcut.

Requires tkinter to be installed. (apt install python-tk)

## Usage

On the first run of the program a file named CONFIG will be created in the directory where the program resides.
Click Config in the menu to set your default save path. This will be where the save dialog starts when saving a file and 
should be the root directory of your recipe folder. 
Not setting this will cause the save dialog to default to the program folder and require unnecessary navigation to
the desired directory to save the first file each session.

Fill out the recipe title, the ingredients, and the directions in the main window.
Use File>Save or Ctrl+s to save. 

The recipe title will be reformatted for use as the file name. It will be converted to all lower case and spaces will be 
changed to underscores.

A bullet point will be added before each ingredient.
Both of these features can be turned off by opening the CONFIG file in a text editor and changing the relevant 
settings from True to False

After saving use File>New or Ctrl+n to clear the entry boxes for the creation of another recipe.
Program help can be found in the Menu

## License

Licensed under [GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
