# Recipe Scribe
A no frills recipe program. Creates recipe files in text format without a database and saves to the specified location.  
Programmed in Python 3.6

![Screenshot](/screenshot/rc_main_window.png?raw=true "Screenshot")

![Screenshot](/screenshot/rc_dark_mode.png?raw=true "Dark mode screenshot")

## Installation

You can download the recipe_scribe_linux_executable tarball for a standalone executable for Linux made with Pyinstaller.
No Windows exe, but you're welcome to make your own using the source files on windows.

Otherwise either clone the repo, or download the zip of the files.
Extract the .zip and move the folder wherever you want to keep it. Make recipe_scribe.py executable and run from the 
command line or make a program shortcut.
No installation is required, all the files are included to run from the extracted folder.

Requires tkinter to be installed if running from source.

#### Installing TKinter
Debian/Ubuntu:
```
sudo apt install python3-pip
pip install tkinter
```
Fedora:
```
sudo dnf install python3-pip
pip install tkinter
```
Arch:
```
sudo pacman -S python-pip
pip install tkinter
```

Tkinter doesn't have to be installed to run the executable.
 
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
If you don't want bullet points before each ingredient you can disable them by 
selecting that item on the Config menu and choosing False.  
Re-enable them by changing it back to True. 

If you don't want the recipe title automatically formatted for use as the filename,
then select that option in the Config menu and choose False.  
This will cause the program to use the recipe name as written for the filename, 
including spaces and capital letters.

Any changes to the configuration require you to restart the application
for them to take effect, as the config file is read at program launch.

Blank lines in the ingredients list will not have a bullet point.
To omit the bullet point from a line of text in the ingredients list, begin the line with a period (.).
The period will be removed automatically when saving the file.

### Ingredients Example
If you enter:  
ingredient 1  
ingredient 2  
ingredient 3  

.For the Gravy  
gravy ingredient 1  
gravy ingredient 2  

The saved file will be:  
• ingredient 1  
• ingredient 2  
• ingredient 3  

For the Gravy  
• gravy ingredient 1  
• gravy ingredient 2  

Unnumbered lines in the directions will be indented 3 spaces.

### Directions example
If you enter:  
    1. This is the first step.<br>
    This is another part of the first step  

The saved file will read:  
    1. This is the first step<br>
    &nbsp;&nbsp;&nbsp;&nbsp;This is another part of the first step  
   

After saving use File>New or Ctrl+n to clear the entry boxes for the creation of another recipe.
Program help can be found in the Menu

## Notes
Now supporting light and dark modes. Change to dark mode using the config menu and restart the application.
Initial window size now calculated based on screen geometry.
The entry boxes now scale properly when resizing the window.

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
