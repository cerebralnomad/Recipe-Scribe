#!/usr/bin/env python3.6
'''
Recipe Creator
version 0.3.2
Basic no frills GUI Program for creating and saving recipes.
Written in Python 3.6 and TKinter
 
Copyright (C) 2019 Clay Davenport
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''


import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import Menu
from tkinter import messagebox as msg
from tkinter import filedialog
import re
import configparser
from os import path
import ToolTip as tt
from HelpText import help_text
from AboutText import about_text


config = configparser.ConfigParser()

if path.exists("CONFIG"):
    config.read("CONFIG")
    save_path = config.get('DefaultSavePath', 'save_path')
    use_bp = config.get('UseBulletPoints', 'use_bp')
    fn_format = config.get('FormatFileName', 'fn_format')
else:
    file = open('CONFIG', 'w+')
    file.close()
    save_path = "None"
    use_bp = "True"
    fn_format = "True"
    config.add_section("DefaultSavePath")
    config.add_section("UseBulletPoints")
    config.add_section("FormatFileName")
    config.set("DefaultSavePath", "save_path", "None")
    config.set("UseBulletPoints", "use_bp", "True")
    config.set("FormatFileName", "fn_format", "True")
    with open("CONFIG", "w+") as configfile:
        config.write(configfile) 

class MAIN():
    '''
    The main window where the recipe information is entered
    '''
    def __init__(self, master):
        '''
        Create the root window, call the methods to create
        key bindings and all the widgets
        '''
        self.frame = tk.Frame(root)
        self.frame.pack(fill = 'both', expand = True, side = 'top')
        #self.frame.configure(background = 'gray83')
        self.frame.configure(background = 'gray83')
        self.frame.rowconfigure(1, weight = 1)
        self.frame.columnconfigure(0, weight = 1)
        self.frame.columnconfigure(1, weight = 3)
        master.title('Recipe Creator') 
        self.bind_keys()
        self.create_widgets()

    def bind_keys(self):
        '''
        Set the bindings for the keyboard shortcuts to the menu items
        '''
        root.bind('<Control-s>', self._save)
        root.bind('<Control-n>', self._new)
        root.bind('<Control-q>', self._quit)
        root.bind('<Control-h>', HelpWindow)
        root.bind('<Control-c>', DefaultPath)

    def _quit(self, event='q'):
        '''
        Function to exit GUI cleanly
        Bound to the Exit command on the file menu
        '''
        root.quit()
        root.destroy()
        exit()

    def focus_next_widget(self, event):
        '''
        Allows the use of the TAB key to advance to the next entry field
        TAB must be pressed twice for the cursor to show. Reason for this currently unknown
        '''
        event.widget.tk_focusNext().focus()
        return 'break'

    def _save(self, event='s'):
        '''
        _save opens the save dialog box. Not sure if the code is proper here
        Without the event parameter, there's an error using the keyboard
        shortcut (1 param expected, 2 given)
        Without giving event a default value, there's an error when clicking the
        menu item (2 param expected, 1 given)
        '''

        # Retrieve the name of the recipe from the title box widget
        recipe_name = self.title_entered.get()
        # reformat the recipe name for use as the file name
        if fn_format == "True" or fn_format == "true":
            file_name = recipe_name.lstrip().lower().replace(' ', '_')
        else:
            file_name = recipe_name
        # split the ingredient list based on newline
        ingredients = self.ingredients.get(1.0, 'end-1c').split('\n')
        directions = self.directions.get(1.0, 'end')

        if save_path is None:
            file = filedialog.asksaveasfile(mode='w', initialfile=file_name,
                                            defaultextension=".txt")
        else:
            file = filedialog.asksaveasfile(mode='w', initialfile=file_name,
                                            defaultextension=".txt", initialdir=save_path)
        if file is None:
            return
        file.write('\n')
        file.write(recipe_name)
        file.write('\n\n')
        file.write('Ingredients')
        file.write('\n\n')
        # Make sure blank lines in ingredients are not bullet pointed
        if use_bp =="True" or use_bp == "true":
            for i in ingredients:
                line = i
                if not re.match('\w', line): # using re import for regex search to see if line contains letters or numbers
                    file.write(line +'\n')
                else:
                    file.write('• ' + line + '\n')  # Prepend each ingredient with a bullet point
        else:
            for i in ingredients:
                line = i
                file.write(line + '\n')
        file.write('\n')
        file.write('Directions')
        file.write('\n\n')
        file.write(directions)
        file.write("\n\n\n")
        file.close()

    # Function to clear the text for entering another recipe.
    # See comments for _save for explanation of the event parameter

    def _new(self, event='e'):
        '''
        Function to clear the text for entering another recipe.
        See comments for _save for explanation of the event parameter
        '''
        self.title_entered.delete(0, 'end')
        self.ingredients.delete(1.0, 'end')
        self.directions.delete(1.0, 'end')
        self.title_entered.focus()  # Place cursor back into the title entry box

    def create_widgets(self):
        '''
        Long method to create all widgets on the root window
        '''

        # Creating a Menu Bar

        menu_bar = Menu(root)
        root.config(menu=menu_bar)
        menu_bar.config(background = 'gray83')
        # Code for the cascading File menu
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label='New   Ctrl+n', command=self._new)
        file_menu.add_separator()
        file_menu.add_command(label='Save  Ctrl+s', command=self._save)
        file_menu.add_separator()
        file_menu.add_command(label='Quit  Ctrl+q', command=self._quit)
        menu_bar.add_cascade(label='File', menu=file_menu)

        # Code for the cascading Help menu
        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label='Program Help  Ctrl+h', command=HelpWindow)
        help_menu.add_separator()
        help_menu.add_command(label='About', command=AboutWindow)
        menu_bar.add_cascade(label='Help', menu=help_menu)

        # Code for the individual menu buttons with no cascade
        menu_bar.add_command(label='Config', command=DefaultPath)

        # Top frame for the recipe name entry
        self.title_frame = ttk.LabelFrame(self.frame, text=' Enter Recipe Title ')
        self.title_frame.grid(column=0, row=0, columnspan=2, padx=8, pady=4, sticky='W')

        # Left frame for the ingredients list
        self.ing_frame = ttk.LabelFrame(self.frame, text=' Ingredients ')
        self.ing_frame.grid(column=0, row=1, padx=8, pady=4, sticky = 'news')
        self.ing_frame.rowconfigure(0, weight = 1)
        self.ing_frame.columnconfigure(0, weight = 1)

        # Right frame for the directions
        self.dir_frame = ttk.LabelFrame(self.frame, text=' Directions ')
        self.dir_frame.grid(column=1, row=1, padx=8, pady=4, sticky='nwes')
        self.dir_frame.rowconfigure(0, weight = 1)
        self.dir_frame.columnconfigure(0, weight = 1)

        # Adding a text box entry widget for the recipe title
        self.title = tk.StringVar()
        self.title_entered = tk.Entry(self.title_frame, width=75, textvariable=self.title,
                                      bd=5, relief=tk.RIDGE)
        self.title_entered.grid(column=0, row=2, padx=8, pady=(3, 8), sticky='W')
        self.title_entered.bind("<Tab>", self.focus_next_widget)
        tt.create_ToolTip(self.title_entered, 'Enter the title of the recipe here')

        # Add a scroll box for ingredients
        self.ingredients = scrolledtext.ScrolledText(self.ing_frame, width = 30, bd=5,\
                wrap=tk.WORD, relief=tk.RIDGE)
        self.ingredients.grid(column=0, row=0, padx=8, pady=(0, 20), sticky=tk.N+tk.S+tk.E+tk.W)
        self.ingredients.bind("<Tab>", self.focus_next_widget)
        tt.create_ToolTip(self.ingredients, 'Enter ingredients here, one per line')

        # Add a scroll text box for directions
        self.directions = scrolledtext.ScrolledText(self.dir_frame, bd=5,\
                wrap=tk.WORD, relief=tk.RIDGE)
        self.directions.grid(column=0, row=0, padx=8, pady=(0, 20), sticky=tk.N+tk.S+tk.E+tk.W)
        tt.create_ToolTip(self.directions, 'Enter the recipe instructions here')

        self.title_entered.focus()  # Place cursor into the title entry box

class DefaultPath():
    '''
    Brings up the dialog box to set a default save path for use as
    a starting save location when saving a file
    '''
    def __init__(self):
        '''
        Create the new window and the two buttons to
        either select location or cancel
        '''

        path = save_path
        self.pathwin = tk.Tk()
        self.pathwin.title('Set Default Save Path')
        if path is None:
            self.current_loc = ttk.Label(self.pathwin, text = 'The current default save path is not set.')
            self.current_loc.grid(column=1, row=1, columnspan=2, padx=10, pady=(15, 0), sticky='WE')
        else:
            self.current_loc = ttk.Label(self.pathwin, text = "The current save path is set to '{}':\n ".format(path))
            self.current_loc.grid(column=1, row=1, columnspan=2, padx=(10), pady=(15, 0), sticky='WE')
        self.msg = ttk.Label(self.pathwin, text='Click Browse to select your default save location')
        self.msg.grid(column=1, row=2, columnspan=2, padx=10, pady=(10, 25), sticky='WE')
        self.button = ttk.Button(self.pathwin, text=' Browse ', command=self.set_path)
        self.button.grid(column=1, row=3, padx=10, pady=(0, 25), sticky='WE')
        self.cancel = ttk.Button(self.pathwin, text=' Cancel ', command=self.pathwin.destroy)
        self.cancel.grid(column=2, row=3, padx=10, pady=(0, 25), sticky='WE')

    def set_path(self):
        '''
        Get the chosen location and write it to CONFIG so it is remembered
        when the program is run in the future
        '''
        path = filedialog.askdirectory()
        config.set('DefaultSavePath', 'save_path', path)
        with open('CONFIG', 'w+') as configfile:
            config.write(configfile)
        self.msgbox()

    def msgbox(self):
        '''
        Confirmation popup that the default path was saved
        '''
        msg.showinfo(
            'Default Save Path Set', 'Your default save \npath has been set.\n\nThis will take effect \nthe next time you run \nthe program'
            )

class HelpWindow():
    '''
    Pops up the window with the program usage information
    '''
    def __init__(self, master=None):
        '''
        Create the new window to hold the help text
        '''
        self.helpwin = tk.Tk()
        self.helpwin.title('Program Usage')
        self.help_text()

    def help_text(self):
        '''
        Create a scrollbox to hold the help information, open the external
        help.txt file and read the contents into the scrollbox
        '''
        hscroll_w = 80
        hscroll_h = 40
        self.help_box = scrolledtext.ScrolledText(self.helpwin,
                                                  width=hscroll_w, height=hscroll_h,
                                                  wrap=tk.WORD, bd=5, relief=tk.RIDGE)
        self.help_box.grid(column=0, row=0, padx=8, pady=(0, 20))
        self.help_box.insert(1.0, help_text)
        self.help_button = tk.Button(self.helpwin, text='Close', command=self.helpwin.destroy)
        self.help_button.grid(column=0, row=1, padx=50, pady=(0, 15), sticky='WE')

class AboutWindow():
    '''
    Pops up the window showing version and license info
    '''
    def __init__(self):
        '''
        Create the window to display the 'about' information
        '''
        self.aboutwin = tk.Tk()
        self.aboutwin.title('About')
        self.about_text()

    def about_text(self):
        '''
        Create a text box to hold the about information, open the external
        file ABOUT, and read the contents into the text box
        '''
        width = 75
        height = 20
        self.about_box = tk.Text(self.aboutwin, width=width, height=height,
                                 wrap=tk.WORD, bd=5, relief=tk.RIDGE)
        self.about_box.grid(column=0, row=0, padx=8, pady=(0, 20))
        self.about_box.insert(1.0, about_text)
        self.about_button = tk.Button(self.aboutwin, text='Close', command=self.aboutwin.destroy)
        self.about_button.grid(column=0, row=1, padx=50, pady=(0, 15), sticky='WE')


#=============
#Start GUI
#=============
root = tk.Tk()
width = int(root.winfo_screenwidth() / 2)
height = int(root.winfo_screenheight() / 1.4)
root.geometry('%sx%s' % (width, height))
root.configure(background = 'gray83')
root.rowconfigure(0, weight = 1)
root.rowconfigure(1, weight = 1)
root.columnconfigure(0, weight = 1)
root.columnconfigure(1, weight = 3)
style = ttk.Style()
style.configure('TLabelframe', background = 'gray83')
style.configure('TLabelframe.Label', background = 'gray83')
main = MAIN(root)    # Create an instance of the MAIN class
root.mainloop()
