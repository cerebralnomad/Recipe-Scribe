# Recipe Scribe
A no frills recipe program. Creates recipes as text files without a database and saves to your specified location.<br>  
Includes a built in search to find recipes in your collection by name or partial name or ingredient.<br>
Allows editing existing recipes from within the app without needing to open in a text editor.

* Automatically adds bullet points to ingredients (configurable)
* Automatic indentation of directions (configurable)
* Automatic formatting of the title to the filename (configurable)
* Light or Dark mode

Version 2.0 is considered feature complete at this time. <br>
I don't plan any further development for the forseeable future, barring any bugs found.<br>
Get the standlone Linux executable or the AppImage from the [Releases Page](https://github.com/cerebralnomad/Recipe-Scribe/releases/tag/v2.0.1-stable)<br>
A Flatpak is now available on [Flathub](https://flathub.org/apps/com.cerebralnomad.recipescribe).<br>
There might be a snap later.<br>

[![Flathub Icon](https://flathub.org/api/badge?locale=en)](https://flathub.org/apps/com.cerebralnomad.recipescribe)
 
![Screenshot](/screenshot/rs_main_window.png?raw=true "Screenshot")
![Screenshot](/screenshot/rs_dark_mode.png?raw=true "Dark mode screenshot")
![Screenshot](/screenshot/rs_search_window.png?raw=true "Search Window Screenshot")

## Installation
### Flatpak
The simplest and recommended method to run the program is from the Flatpak.  
If you haven't used Flatpaks, you may need to install it, at least on Ubuntu.
```
sudo apt install flatpak
```
Then add the flatpak repo:
```
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
```
Then either install from the command line:
```
flatpak install com.cerebralnomad.recipescribe
```
Or from Flathub using the link below:

[![Flathub Icon](https://flathub.org/api/badge?locale=en)](https://flathub.org/apps/com.cerebralnomad.recipescribe)

### AppImage
Download the Appimage from the [Releases](https://github.com/cerebralnomad/Recipe-Scribe/releases/tag/v2.0.1-stable) page.  
Extract the AppImage wherever you want and make it executable.

### Standalone executable for Linux
There is also a standalone executable made with PyInstaller available on the [Releases](https://github.com/cerebralnomad/Recipe-Scribe/releases/tag/v2.0.1-stable) page.  
Extract the binary and make it executable.  
This method has only been tested on Ubuntu flavors.

### Running from source
There is also a zip of the source files on the [Releases](https://github.com/cerebralnomad/Recipe-Scribe/releases/tag/v2.0.1-stable) page.  
If you want to run it from source, it requires that TKinter be installed seperately on the system.  
That's up to you, btu there's no real reason to run it from source.  
 
## Usage

On the first run of the program a file named recipe_scribe.conf will be created in ~/.config.  
Click Config in the menu to set your default save path.  
This will be where the save dialog starts when saving a file and should be the root directory of your recipe folder.  
Not setting this will cause the save dialog to default to the program folder and require unnecessary navigation to
the desired directory to save the first file each session.  
This is required to be set for the search function to work.

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

Any changes to the configuration will trigger a program restart so they take effect immediately.

Blank lines in the ingredients list will not have a bullet point.
To omit the bullet point from a line of text in the ingredients list, begin the line with a period (.).
The period will be removed automatically when saving the file.

Likewise, any line in the Directions beginning with a period will not be indented.
This allows you to include Notes or Links in the directions without having them indented,
making the saved file look better.

### Ingredients Example
If you enter:  
> ingredient 1  
> ingredient 2  
> ingredient 3  
>
> .For the Gravy  
> gravy ingredient 1  
> gravy ingredient 2  

The saved file will be:  
> • ingredient 1  
> • ingredient 2  
> • ingredient 3  
>
> For the Gravy  
> • gravy ingredient 1  
> • gravy ingredient 2  

Unnumbered lines in the directions will be indented 3 spaces unless preceeded by a period.

### Directions example
If you enter: 
```
1. This is the first step.  
This is another part of the first step

2. This is the second step.
A continuation of the second step.

.Link to the recipe or youtube video
```
The saved file will read:  
```
1. This is the first step<br>
   This is another part of the first step

2. This is the second step.
   A continuation of the second step.

Link to the recipe or youtube video
```
After saving use File>New or Ctrl+n to clear the entry boxes for the creation of another recipe.
Program help can be found in the Menu

### Search Function Usage
You must have a default save path set to use the recipe search.  
It uses this path as the location to perform the search.

To search your recipies from the program, click Search Recipies in the menubar.  
Type your search term in the search box and click either the Ingredient Search or Title Search button.  
The Title Search will look for the search term in the titles of all your recipes.  
The Ingredient Search will search the contents of every recipe file in your collection for the search term.  
Searches are not case sensitive.

The search results will display in the left hand pane. Click on a result and the recipe will be displayed in the right pane.  
You can edit the recipe from the program if you need to. Simply make your changes and click the Save button.  
Clicking the Save button will immediately overwrite the existing file with the contents of the window displaying the recipe.  
There is no confirmation dialog.

Single word searches work best and title searches only support single words.  
When searching for two words, results will include all files which contain both words.  
This can greatly increase results in some cases.  
Searching for more than two words is not supported and will return an error message as the results.

## Notes
Now supporting light and dark modes.<br>
Change to dark mode using the config menu.<br>
Initial window size now calculated based on screen geometry.<br>
Can be set to start fullscreen in the config menu.<br>
The entry boxes now scale properly when resizing the window.<br>
Added the search feature with editing capabilities.<br>

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
