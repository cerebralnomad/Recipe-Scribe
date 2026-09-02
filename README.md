# Recipe Scribe

A no frills recipe program. Creates recipes as text files without a database and saves them
to your specified location.<br>
Organize your collection into categories, and search by title, content, or both, with any
number of search terms.<br>
Allows editing existing recipes from within the app without needing to open a text editor.

* Organize recipes into categories, managed from the Config menu
* Search by title, content, or both, filtered by category if you like, with no limit on
  the number of search terms
* Automatically adds bullet points to ingredients (configurable)
* Automatic indentation of directions, correctly aligned even at step 10 and beyond
  (configurable)
* Automatic formatting of the title to the filename (configurable)
* Light or Dark mode

Version 3.0 is a complete rewrite from Tkinter to the Qt toolkit (PyQt6), adding categories
and a much more capable search. I don't plan any further major development for the
foreseeable future, barring any bugs found.<br>
A Flatpak is available on [Flathub](https://flathub.org/apps/com.cerebralnomad.recipescribe).

[![Flathub Icon](https://flathub.org/api/badge?locale=en)](https://flathub.org/apps/com.cerebralnomad.recipescribe)

![Screenshot](/screenshot/rs_main_window.png?raw=true "Screenshot")
![Screenshot](/screenshot/rs_dark_mode.png?raw=true "Dark mode screenshot")
![Screenshot](/screenshot/rs_search_window.png?raw=true "Search Window Screenshot")

## Installation

### Flatpak
The simplest and recommended method to run the program is from the Flatpak.
If you haven't used Flatpaks before, you may need to install it, at least on Ubuntu.
```
sudo apt install flatpak
```
Then add the Flathub repo:
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
An AppImage for version 3.0 (Qt) is not yet available.
The version 2.0.1 AppImage, still using Tkinter, remains available on the
[Releases](https://github.com/cerebralnomad/Recipe-Scribe/releases/tag/v2.0.1-stable) page
in the meantime.

### Running from source
You can run from source, but it's best to do so in a Python virtual environment.
```
git clone https://github.com/cerebralnomad/Recipe-Scribe.git
cd Recipe-Scribe
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```
Requires Python 3.10 or newer.

## Usage

On the first run of the program a file named `recipe_scribe_qt.conf` will be created in
`~/.config`.<br>
Click Config in the menu to set your default save path.
This will be where the save dialog starts when saving a file, and should be the root
directory of your recipe folder.
Not setting this will cause the save dialog to default to wherever it last was, and require
unnecessary navigation to the desired directory the first time you save each session.
This is required to be set for the search function to work.

Fill out the recipe title, category, ingredients, and directions in the main window.
Use File > Save or Ctrl+S to save.

The recipe title will be reformatted for use as the file name. It will be converted to all
lower case and spaces will be changed to underscores. This can be disabled from the Config
menu if you'd rather the filename match the title exactly.

### Category

Choose a category from the dropdown, or type a new one directly into the box. If you type a
category that isn't in your list yet, you'll be asked whether to add it when you save.

You can also manage your category list at any time from Config > Manage Categories - add,
rename, or remove categories in one session, with a Done/Cancel step so you can back out of
changes before they're saved.

Renaming or removing a category only changes the list you pick from going forward - recipes
you've already saved keep whatever category text was written into them at the time.

### Ingredients

A bullet point will be added before each ingredient. Only place one ingredient per line - a
new line is created when you press Enter, not when a long ingredient wraps visually.

If you don't want bullet points before each ingredient, disable them from the Config menu.

Blank lines in the ingredients list will not have a bullet point.
To omit the bullet point from a line of text in the ingredients list, begin the line with a
period (`.`). The period will be removed automatically when saving the file. This is useful
for section headers, such as marking out a sub-recipe within the ingredients.

#### Ingredients Example
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

### Directions

Unnumbered lines in the directions will be automatically indented so they line up under the
step they belong to - this now stays correctly aligned at step 10 and beyond, not just
single-digit steps.

Any line in the Directions beginning with a period will not be indented. This allows you to
include notes or links in the directions without having them indented, making the saved file
look better.

#### Directions Example
If you enter:
```
1. This is the first step.
This is another part of the first step

2. This is the second step.
A continuation of the second step.

.Link to the recipe or a video
```
The saved file will read:
```
1. This is the first step.
   This is another part of the first step

2. This is the second step.
   A continuation of the second step.

Link to the recipe or a video
```

After saving, use File > New or Ctrl+N to clear the entry boxes for the creation of another
recipe. Program help can be found in the Help menu at any time.

### Recipe Search

You must have a default save path set to use the recipe search.
It uses this path as the location to perform the search.

Click "Search Recipes" in the menu bar to switch to the search page. Type a search term into
the search box - any number of words is supported, and a recipe must contain all of them to
match. Use the Scope dropdown to search titles only, recipe content only, or both. Use the
Category dropdown to narrow results to a single category, or leave the search box empty and
pick a category to browse everything filed under it. Searches are not case sensitive.

The search results display in the left hand pane, along with each recipe's category if it has
one. Click a result and the recipe displays in the right pane, where you can edit both its
text and its category. Click Save Edits to write your changes - this immediately overwrites
the existing file. There is no confirmation dialog.

### Config Menu

| Item | Effect |
|---|---|
| Set Default Save Path | Choose where recipes are saved and searched |
| Use Bullet Points | Toggle ingredient bullet points (restarts the program) |
| Format Filename | Toggle automatic filename formatting (restarts the program) |
| Use Dark Mode | Toggle light/dark theme (restarts the program) |
| Start Fullscreen | Start the program fullscreen next launch (does not restart now) |
| Manage Categories | Add, rename, or remove categories |

## Notes
Now supporting recipe categories, managed from the Config menu and filterable in search.<br>
Search rewritten to support any number of search terms, searching title, content, or both.<br>
Fixed a longstanding bug where direction step indentation misaligned from step 10 onward.<br>
Supports light and dark modes.<br>
Can be set to start fullscreen from the Config menu.<br>
The entry boxes scale properly when resizing the window.<br>

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
